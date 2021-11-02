## Daymap Getter
### Gets things from the GIHS Daymap server through the magic of webscraping.
---
## HTTP Spec

* GET /lessons
    
    *Gets all lessons for the user in the defined time range.*
    * JSON Payload:
        
        Always contains:
        * `username` (string) The person's username.
        * `from` (UTC Unix Timestamp) Start date for queried lesson range (time is ignored)
        * `to` (UTC Unix Timestamp) End date for queried lesson range (time is ignored)

        Then, either:
        * `password` (string) The person's password, in plaintext.
        *This variant should be used if no session cookies have been stored on the server. It takes about 3x as long to complete a request because of all the authentication that has to occur with Daymap.*
    
        Or:
        * `cookies` (object) Daymap's session cookies in a JSON object (key-value pair)
        *This *
    * Returns:
        * 200 OK - Lesson query successful
        * 402 Bad Gateway - Daymap didn't respond properly
        * 400 Bad Request - JSON Payload was invalid

        <br>

        **Example request with user/pass combo:**
        ```jsonc
        {
            "username": "someuser",
            "password": "PlaintextPassword",
            "from": 1234567,
            "to": 7654321
        }
        ```
        Response:
        ```jsonc
        {
            "data": [
                {
                    // example lesson
                    "name": "something", // raw Daymap lesson name
                    "id": 12345678, // Daymap internal id
                    "start": 1234567890, // unix timestamp
                    "finish": 9876543210, // unix timestamp
                    "attendance": "NotSet", // Daymap attendance enum
                    "resources": false,
                    "links": [ 
                        // any material links teacher set
                        {
                            "label": "some plan",
                            // these ID's allow content to be fetched
                            "planId": 123456,
                            "eventId": 654321
                        }
                    ]
                },
                { /* another lesson */ },
                { /* another lesson */ }
            ],
            "cookies": {
                // Daymap identity cookies, keep these
                "name": "value"
            }
        }
        ```

        **Example request with cookies:**
        ```jsonc
        {
            "username": "someuser",
            "cookies": {
                /* Daymap identity cookies */
            },
            "from": 1234567,
            "to": 7654321
        }
        ```
        Response:
        ```jsonc
        {
            "data": [
                { /* lesson */ },
                { /* lesson */ },
                { /* lesson */ }
            ]
            // notice how no cookies are returned if the passed ones are valid
        }
        ```