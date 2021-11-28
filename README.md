## Daymap Getter
### Gets things from the GIHS Daymap server through the magic of webscraping.
---
## HTTP Spec

Note: If you're accessing an endpoint, access it with `/` at the end. It skips an unnecessary redirect!

* POST `/lessons/`
    
    *Gets all lessons for the user in the defined time range.*
    * JSON Payload:
        
        Always contains:
        * `username` (string) The person's username.
        * `start` (UTC Unix Timestamp) Start date for queried lesson range (time is ignored)
        * `end` (UTC Unix Timestamp) End date for queried lesson range (time is ignored)

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
                    "attendance": "NotSet" // Daymap attendance enum
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

* POST `/lessons/plans/`
    
    *Gets lesson plans for a lesson.*
    * JSON Payload:
        
        Always contains:
        * `username` (string) The person's username.
        * `lesson_id` (int) The ID of the lesson to query plans for.

        Then, either:
        * `password` (string) The person's password, in plaintext.
        *This variant should be used if no session cookies have been stored on the server. It takes about 3x as long to complete a request because of all the authentication that has to occur with Daymap.*
    
        Or:
        * `cookies` (object) Daymap's session cookies in a JSON object (key-value pair)
        *This *
    * Returns:
        * 200 OK - Plan query successful
        * 402 Bad Gateway - Daymap didn't respond properly
        * 400 Bad Request - JSON Payload was invalid

        <br>

        **Example request with user/pass combo:**
        ```jsonc
        {
            "username": "someuser",
            "password": "PlaintextPassword",
            "lesson_id": 123456
        }
        ```
        Response:
        ```jsonc
        {
            "data": {
                "notes": [
                    {
                        // fields can disappear from here if they're not set in daymap
                        "title": "Note Title",
                        "content": "Blah blah blah, we're doing learning today...",
                        "links": {
                            // links fished out from content
                            "Video You Should Watch": "https://youtube.com/(something)",
                        },
                        "files": {
                            // this is a daymap attachment id, a download url can be constructed using it
                            "CoolDocument.docx": 123456
                        }
                    },
                    { /* another note on same lesson */ },
                    { /* another note on same lesson */ },
                ],
                "extra_files": {
                    // files not belonging to any specific note, just placed out in the void
                    "ExtraDocument.pdf": 111222
                }
            },
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
            "lesson_id": 123456
        }
        ```
        Response:
        ```jsonc
        {
            "data": { 
                /* same as above */
            }
            // notice how no cookies are returned if the passed ones are valid
        }
        ```

* POST `/messages/`
    
    *Gets all messages for the user, ever.*
    * JSON Payload:
        
        Always contains:
        * `username` (string) The person's username.

        Then, either:
        * `password` (string) The person's password, in plaintext.
        *This variant should be used if no session cookies have been stored on the server. It takes about 3x as long to complete a request because of all the authentication that has to occur with Daymap.*
    
        Or:
        * `cookies` (object) Daymap's session cookies in a JSON object (key-value pair)
        *This *
    * Returns:
        * 200 OK - Message query successful
        * 402 Bad Gateway - Daymap didn't respond properly
        * 400 Bad Request - JSON Payload was invalid

        <br>

        **Example request with user/pass combo:**
        ```jsonc
        {
            "username": "someuser",
            "password": "PlaintextPassword",
        }
        ```
        Response:
        ```jsonc
        {
            "data": [
                {
                    "id": "123456",
                    "sender": "John DOE (doej)",
                    "date": "Tue 7:30 PM",
                    "subject": "This is the subject of a test message!"
                },
                { /* another message */ },
                { /* another message */ }
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
            }
        }
        ```
        Response:
        ```jsonc
        {
            "data": [
                { /* message */ },
                { /* message */ },
                { /* message */ }
            ]
            // notice how no cookies are returned if the passed ones are valid
        }
        ```

* POST `/tasks/`
    
    *Gets all current tasks for the user.*
    * JSON Payload:
        
        Always contains:
        * `username` (string) The person's username.

        Then, either:
        * `password` (string) The person's password, in plaintext.
        *This variant should be used if no session cookies have been stored on the server. It takes about 3x as long to complete a request because of all the authentication that has to occur with Daymap.*
    
        Or:
        * `cookies` (object) Daymap's session cookies in a JSON object (key-value pair)
        *This *
    * Returns:
        * 200 OK - Tasks query successful
        * 402 Bad Gateway - Daymap didn't respond properly
        * 400 Bad Request - JSON Payload was invalid

        <br>

        **Example request with user/pass combo:**
        ```jsonc
        {
            "username": "someuser",
            "password": "PlaintextPassword",
        }
        ```
        Response:
        ```jsonc
        {
            "data": [
                {
                    "id": "12345",
                    "title": "Example Task",
                    "lessonName": "10 Digital Technology1A",
                    "type": "summative", // can be: "summative", "formative", "(something else)"
                    "dueDate": 1624924800, // unix timestamp of duedate
                    // now, there will either be an "alert" field, a "grades" field, or neither. not both.
                    "alert": "Overdue. Work has not been received",
                    // or
                    "grades": {
                        // these fields may or may not spontaneously disappear, idk
                        "grade": "E-",
                        "mark": "1 / 100",
                        "comments": "This is the worst assignment I've ever seen."
                    }
                },
                { /* another task */ },
                { /* another task */ }
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
            }
        }
        ```
        Response:
        ```jsonc
        {
            "data": [
                { /* task */ },
                { /* task */ },
                { /* task */ }
            ]
            // notice how no cookies are returned if the passed ones are valid
        }
        ```
