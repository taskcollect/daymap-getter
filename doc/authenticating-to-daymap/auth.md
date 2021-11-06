This file is an archive of my pilgrimage to talking to Daymap. Don't expect it to be good, but it should maybe explain how authentication works, sort of. 

There's a [proof of concept Python script](./auth.py) that does this all. And so far, I haven't been able to get it working with anything other than Python. The problem is somewhere in the NTLM handshake, only requests_ntlm can do it properly.

Happy reading.

---

# Authenticating to Daymap

We want to access Daymap. 

Before, it used to use NTLM, but of course, as with all things,
fixing what's already functioning seems to be the standard. So now it doesn't work. Great.

### What we know so far:
* It uses OpenIDConnect somehow, and the specification exists [over here]( https://openid.net/specs/openid-connect-basic-1_0.html#AuthenticationRequest)...
* https://daymap.gihs.sa.edu.au/daymapidentity/login is the login url that provides the login script
* https://daymap.gihs.sa.edu.au/daymapidentity/content/scripts/login.js is the login script


### Where to begin?
Since we know almost nothing about nothing, let's start off by exploring the redirects that happen when we try to access the target page on Daymap. 

#### What happens when we request the target URL
1. The client requests their target URL (eg /daymap/dayplan.aspx)
2. The server responds with a 302 to https://daymap.gihs.sa.edu.au/daymapidentity/login
3. The client requests https://daymap.gihs.sa.edu.au/daymapidentity/login as it has been told, from the 302
4. The server responds with a 200, and sends a bunch of stuff, way more than just a login form.
   * At this point, some scripts are requested and run from hrefs in script tags:
     * ## [master.js](https://daymap.gihs.sa.edu.au/daymapidentity/content/scripts/master.js)
       which handles the decoding of the hardcoded information in the document body.

       It sounds complicated, but it isn't.

       All you need to know is that there's about two elements that arrive alongside
       the login document, that look something like this:

       ```html
       <script id="modelJson" type="application/json">data here blah blah</script>
       <script id="pageJson" type="application/json">more data here, js object</script>
       ```
       Keep im mind, even though these are `script` tags, they don't really do anything.
       They only exist there to literally carry information. Placeholders, if you will.

       `master.js` is responsible from extracting the information from these.
       I'm not going to bother explaining the nitty gritty of the script, but, in essence, this is
       what it does:

       For the `identityServer` object,
       ```js
       window.identityServer = (function () {
            var modelJson = document.getElementById("modelJson");
            /* parsing of json, decoding etc. */
            return model; // out comes the json object
        })();
       ```
       
       And for the `pageInfo` object,
       ```js
       window.pageInfo = (function () {
            var pageJson = document.getElementById("pageJson");
            if (pageJson) {
                /* parsing of json, decoding etc. */
                return model; // out comes the json object
            }
        })();
        ```
        And that just about wraps up `master.js`. It's small, but important for the others to run.

     * ## [login.js](https://daymap.gihs.sa.edu.au/daymapidentity/content/scripts/login.js)
       which is naturally responsible for handling login. This should run **after** `master.js` has finished.
       
       It registers 
       a `window.onload` function that seems to be there for running the login task.

       This is what the important part of the function looks like:
       ```js
        window.onload = function () {
        // check if a default auth provider is present. if one is found, automatically redirect the user to the href associated with it to log in
        if (pageInfo.clientId !== 'Connect.Web' && pageInfo.defaultAuthProviderUrl && identityServer.externalProviders) {
            var prov = identityServer.externalProviders.find(function (p) {
                return p.text == pageInfo.defaultAuthProviderUrl;
            });

            if (prov && prov.href) {
                location.href = prov.href;
                return false;
            }
        }
       ```

       The handy comment there tells us what this does. That if statement will actually
       always meet the condition if you're accessing it from a browser!

       Keep in mind, this happens *after* [master.js](https://daymap.gihs.sa.edu.au/daymapidentity/content/scripts/master.js)
       script loads some of the hardcoded info into some JS objects.

       Here, `pageInfo.clientId` is `Daymap.Web` which matches
       ```js
       pageInfo.clientId !== 'Connect.Web'
       ```
       Furthermore `pageInfo.defaultAuthProviderUrl` is `Glenunga Windows Auth`, which matches
       ```js
       // this actually evaluates to true because it's a nonempty string
       pageInfo.defaultAuthProviderUrl
       ```
       And finally, the most interesting one, `identityServer.externalProviders`.
       This is actually really important for what is about to happen. It looks something like this:

       ```json
       [
           {
               href: "https://daymap.gihs.sa.edu.au/daymapidentity/external?provider=Glenunga Windows Auth&signin=SOMETHING123", /* this is some id */
               text: "Glenunga Windows Auth",
               type: "Glenunga Windows Auth",
           }
       ]
       ```

       This, also evaluates to `true` in the if statement as it can be converted to a bool (length nonzero).
       
       So now that we've passed the if statement, what happens?
       ```js
        var prov = identityServer.externalProviders.find(function (p) {
            return p.text == pageInfo.defaultAuthProviderUrl;
        });
        ```
        Okay, this might seem confusing, but it's really simple. Remember that list above?
        Let's find an element that has the property `text` equal to `pageInfo.defaultAuthProviderUrl`!

        We alerady know that `pageInfo.defaultAuthProviderUrl` is `Glenunga Windows Auth` so,
        ding ding ding! We get a match with the first element. `prov` is now that object from
        the list above.

        Great! Now, for the next part, which is very simple...
        ```js
        if (prov && prov.href) {
            location.href = prov.href;
            return false;
        }
        ```
        This just redirects the user to `prov.href` and exits the function.

        ### What happened now?
        * The client should be going to the href the server passed along in the hardcoded element.
          ```
          https://daymap.gihs.sa.edu.au/daymapidentity/external?provider=Glenunga Windows Auth&signin=SOMETHING123
          ```
5. So now, we're en-route to `/daymapidentity/external` carrying some sort of weird `signin` parameter.
   
   That's just great... but here's where things get weird. A login form shows up out of nowhere (I don't know how)
   and just asks us for username & password. What?

   There's actually no scripts in the page either, it's all just a mystery.
   
   Either way, we're somehow 302'd to the next destination in our adventure.
   
   TODO: Figure out how this happens

6. Oh yeah, now we're talking! We end up redirected to
   ```
   https://daymap.gihs.sa.edu.au/webauth/?wtrealm=urn:idsrv3&wctx=WsFedOwinState=SOMETHING456&wa=wsignin1.0
   ```
   which doesn't do anyth- OH! IT RETURNS CONTENT! FINALLY! No? Nope. It's not the content we're looking for...
   
   It's some sort of middle-man again, but at least we have some more HTML to work with.
   That document is very small & very interesting. It's just a HTML form of some sort, with a catch for clients
   that have javascript disabled (which submits the form anyways).

   Here's the form:
   ```html
   <form method="POST" name="hiddenform" action="https://daymap.gihs.sa.edu.au/DaymapIdentity/was/client">
        <input type="hidden" name="wa" value="wsignin1.0" />
        <!-- we'll look at this in a bit-->
        <input type="hidden" name="wresult" value="lots and lots of stuff" /> 
        <input type="hidden" name="wctx" value="WsFedOwinState=SOMETHING456" />
    </form>
   ```

   So this essentially sends a POST to `/DaymapIdentity/was/client` with the parameters shown in the inputs... nice.

   But the input named `wresult` contains some really nasty looking data. Don't believe me? Take a look at this bad boy:

   ```html
   &lt;trust:RequestSecurityTokenResponseCollection xmlns:trust=&quot;http://docs.oasis-open.org/ws-sx/ws-trust/200512&quot;>&lt;trust:RequestSecurityTokenResponse Context=&quot;WsFedOwinState=&quot;>&lt;wsp:AppliesTo xmlns:wsp=&quot;http://schemas.xmlsoap.org/ws/2004/09/policy&quot;>&lt;wsa:EndpointReference xmlns:wsa=&quot;http://www.w3.org/2005/08/addressing&quot;>&lt;wsa:Address>urn:idsrv3&lt;/wsa:Address>&lt;/wsa:EndpointReference>&lt;/wsp:AppliesTo>&lt;trust:RequestedSecurityToken>&lt;wsse:BinarySecurityToken ValueType=&quot;urn:ietf:params:oauth:token-type:jwt&quot; EncodingType=&quot;http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary&quot; xmlns:wsse=&quot;http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd&quot;>SOMETHINGELSE789&lt;/wsse:BinarySecurityToken>&lt;/trust:RequestedSecurityToken>&lt;/trust:RequestSecurityTokenResponse>&lt;/trust:RequestSecurityTokenResponseCollection>
   ```

   This looks horrible, but it seems to be URLescaped XML or something (notice `&quot` and `&lt`), so I should probably replace those and try to make sense of it. Here's that:

   ```xml
    <trust:RequestSecurityTokenResponseCollection xmlns:trust="http://docs.oasis-open.org/ws-sx/ws-trust/200512">
        <trust:RequestSecurityTokenResponse Context="WsFedOwinState=SOMETHING456">
            <wsp:AppliesTo xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy">
                <wsa:EndpointReference xmlns:wsa="http://www.w3.org/2005/08/addressing">
                    <wsa:Address>
                        urn:idsrv3
                    </wsa:Address>
                </wsa:EndpointReference>
            </wsp:AppliesTo>
            <trust:RequestedSecurityToken>
                <wsse:BinarySecurityToken 
                    ValueType="urn:ietf:params:oauth:token-type:jwt" 
                    EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary" 
                    xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
                >
                    SOMETHINGELSE789 (this was very long, and in base64)
                </wsse:BinarySecurityToken>
            </trust:RequestedSecurityToken>
        </trust:RequestSecurityTokenResponse>
    </trust:RequestSecurityTokenResponseCollection>
   ```

   Hooray! It's at least readable. There seems to be a lot of URL's about `docs.oasis-open.org` which is
   at least encouraging...

   ### Let's analyze some of the things we've gathered so far.
   * There's this werid property called `WsFedOwinState` that gets sent around everywhere.
     The server gave it to us in step 6's URL parameters.
   * We are somehow 302'd to a page which contains a self-submitting form - a way to make a POST request.
     * The POST url is https://daymap.gihs.sa.edu.au/DaymapIdentity/was/client
     * The POST request contains three parameters:
       * `wa` equal to `wsignin1.0`
       * `wresult` equal to a lot of URLencoded XML (the stuff above)
       * `wctx` equal to `WsFedOwinState=` with the value we get for `WsFedOwinState`

7. And, at this point... I stopped writing this documentation... because I found a working solution.

    What happens here? Nothing interesting. Just another 302 to another form, that POSTs to the `/Daymap` url and returns our content. What's more interesting is how I figured it out.

### So what's the magic secret to figuring out authenticating to Daymap?
* Don't try to understand how it works, because it's all just technologies duct taped together with a few prayers of working.
* Pretend you're a sysadmin that has to migrate the authentication method from pure NTLM to this, why would you do it, and would you bother completely switching technologies? (epic foreshadowing)
* A bit of trickery with fake submitting forms.

So, let's begin the adventure.

* Alright, so we've managed to decypher what the login.js script does and figured out where it redirects us.

* We can even completely skip the login.js script and just construct the URL ourselves since it will always just be the same, with the exception of the parameter `signin`, which we can get from the `/login` response. 

*  Now, there's something that bugged me about the URL. It ended in `external`... the school used to use NTLM for any authentication needed, so maybe this was just NTLM? - said me, at about 11 PM in a particular evening.
  
* Lo and behold, the `/external` endpoint is actually just regular old NTLM! There's already stuff out there that implements NTLM! This basically solves like ~50% of our problem. Now we know where the username and password goes in.

* We know that even after we complete the NTLM handshake, it redirects us to a lot of forms. Cool. Let's submit them like normal. Everything around the actual NTLM handshake is just fluff.

* You'd expect there to be more, but no, not really. Of course, this all doesn't work without retaining cookies so we need to have a persistent session. The upside of this is that unlike how NTLM worked before, now we have session cookies that we can reuse to get instantly authenticated.

* So, that's it. There's a [<b>python file that does all of this</b>](./auth.py), that I wrote in the same 11PM evening. 

### Here's the full method.

* Get your target URL.
* Save the cookies you just got, and go to the 302 URL.
* Stop! Now that you're at `/daymapidentity/login` with a `signin` parameter, just construct a
  URL to `/daymapidentity/external` with the same parameter. You also need `provider` equal to `Glenunga Windows Auth`.
* Perform an NTLM handshake at your constructed URL with your credentials. You'll get a 401 Unauthorized if your credentials are invalid, and a form if you are correct.
* Get the values of the form and POST them at `/DaymapIdentity/was/client`.
* Hopefully get another form back, and POST its values at `/Daymap/`
* Get redirected to the content you're looking for. Good job.
* You should also have a lot of cookies by now, keep them, they keep track of your session. You can provide them if you need other resources.


So, there it is. Just a few days of reverse engineering, and we're good.

Loop Software and GIHS Sysadmins, please stop this madness.

\- Codian