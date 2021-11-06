"""
[ If you don't know what this does, read the included auth.md ]

First working attempt of trying to authenticate with Daymap.

This works! Just run it with lxml and requests_ntlm installed,
and enter your username & password. It should print your name in the end!

- Codian
"""

"""
Helper function to print a response nicely.
Not relevant to the actual authentication.
"""
def show_resp(r):
    return f'response: {r.status_code} {r.reason} ({len(r.history)} redirects)'

# needed for sending HTTP requests, python-specific
import requests
# needed for sending NTLM handshakes, need to implement in JS
import requests_ntlm
# html parser, JS already has one
from lxml import html

# get credentials from user
username = input('username: ')
password = input('password: ')

print()

# useful url's
URL_ROOT = 'https://daymap.gihs.sa.edu.au'
URL_DAYPLAN = f'{URL_ROOT}/daymap/student/dayplan.aspx'

# set up a cookie session, THIS IS INSANELY IMPORTANT! IT WON'T WORK WITHOUT IT!
s = requests.Session()

# send a GET to our desired page
print('stage 1: requesting dayplan page')
s1 = s.get(URL_DAYPLAN)

print(f'stage 1: {show_resp(s1)}')

# get the signin parameter
signin_id = s1.url.split('?signin=')[-1]

print(f'stage 1: extracted internal signin id: "{signin_id}"')

# construct a redirect url using the signin id
URL_STAGE2 = f'{URL_ROOT}/daymapidentity/external?provider=Glenunga%20Windows%20Auth&signin={signin_id}'

# make an ntlm transaction at the constructed url
print(f'\nstage 2: going to {URL_STAGE2}')
s2 = s.get(
    URL_STAGE2, 
    headers={
        'Referer': s1.url # pretend like this is a redirect
    },
    auth=requests_ntlm.HttpNtlmAuth(username, password) # transaction credentials
)

print(f'stage 2: response: {show_resp(s2)}')

if ('Daymap Identity Error' in s2.text):
    print('stage 2: got daymap identity error, uh oh! bailing.')
    # print(s2.text)
    exit(1)

if (s2.status_code != 200):
    # NTLM said no bueno
    print(f'stage 2: status code is non-ok ({s2.status_code} {s2.reason}) - bailing.')
    print('-- are you sure your credentials are valid?')
    exit(1)

if ('<form method="POST"' in s2.text):
    # the body contains a form, a sign of success
    print('stage 2: authentication success! read good form')
else:
    # self explanatory
    print('stage 2: something weird happened, we got HTTP 200 but no form...?')
    exit(1)


print('\nstage 3: parse form using lxml')
s3_tree = html.fromstring(s2.content)

# find all inputs that aren't submits
print('stage 3: enumerate parameters from inputs')
inputs = s3_tree.xpath('//input[@type!="submit"]')

post_payload = {}

for inp in inputs:
    # don't mind this, this just prints them nicely
    print(f'    {inp.name} = "{inp.value if len(inp.value) < 100 else inp.value[:20] + "..."}"')

    # add them to the payload dict
    post_payload[inp.name] = inp.value

URL_STAGE3 = f'{URL_ROOT}/DaymapIdentity/was/client'

print(f'stage 3: sending POST request to {URL_STAGE3}')

# pretend that we're submitting the form by manually POSTing there
s3 = s.post(URL_STAGE3, data=post_payload)

print(f'stage 3: response: {show_resp(s3)}')

# check if everything went correctly
if ('<form' in s3.text):
    print('stage 3: read good form response, ok to proceed')
else:
    print('stage 3: no form, bailing')
    exit(1)

print('\nstage 4: parse form using lxml')
s4_tree = html.fromstring(s3.content)

print('stage 4: enumerate parameters from inputs')
inputs = s4_tree.xpath('//input')

# same as before
post_payload = {}

for inp in inputs:
    # don't mind this, this just prints them nicely
    print(f'    {inp.name} = "{inp.value if len(inp.value) < 100 else inp.value[:20] + "..."}"')

    # add them to the payload dict
    post_payload[inp.name] = inp.value


URL_STAGE4 = f'{URL_ROOT}/Daymap/'

print(f'stage 4: sending POST request to {URL_STAGE4}')

# pretend that we're submitting the form by manually POSTing there
s4 = s.post(URL_STAGE4, data=post_payload)

print(f'stage 4: response: {show_resp(s4)}')

# at this point s4 should contain our target document! yay!

if ('Day Plan' in s4.text):
    # run a quick test
    print('stage 4: good read on dayplan! success!')

    print("\nas a test, let's get your name...")

    search_string = "window['_userFullName'] = \""

    name = s4.text[s4.text.find(search_string):].split(search_string)[-1].split('";')[0]

    print(f'\nOkay, judging by my calculations, you should be called...\n')
    print(f'    {name}')
    print("\nIf you're not called that, well... yikes.")
else:
    print("stage 4: didn't find 'Day Plan' in document. success is unknown, check for yourself")