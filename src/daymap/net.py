
from typing import Tuple

import requests
import requests_ntlm
import lxml.html

URL_ROOT = 'https://daymap.gihs.sa.edu.au'
URL_DAYPLAN = f'{URL_ROOT}/daymap/student/dayplan.aspx'
URL_SLASHDAYMAP = f'{URL_ROOT}/Daymap/'
URL_DAYMAPIDENTITY = f'{URL_ROOT}/DaymapIdentity/was/client'


# exception for when daymap messed up
class ServerFault(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# something unexpected happened, daymap's api probably changed ;-;
class OurFault(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# the user just didn't enter the correct credentials, what can ya do?
class InvalidCredentials(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# request a resource
# either provide session and no user/pass or the opposite
# pass blank url to get /Daymap
def get_daymap_resource(
    url: str,
    session: requests.Session = None,
    username: str = None,
    password: str = None,
) -> Tuple[requests.Response, requests.Session]:
    if session is None:
        session = requests.Session()
    elif len(session.cookies) > 0:
        # this cookie jar has some cookies, maybe try to do a fast auth
        try:
            return session.get(url), session
        except:
            # nope, that went horribly wrong, I guess we need to auth after all
            # also make a new session while we're at it
            session = requests.Session()

    if username is None or password is None:
        raise InvalidCredentials("missing user or password; fast auth not possible")
    

    resp1 = session.get(URL_DAYPLAN)
    signin_id = resp1.url.split('?signin=')[-1]

    URL_NTLMTARGET = f'{URL_ROOT}/daymapidentity/external?provider=Glenunga%20Windows%20Auth&signin={signin_id}'

    # make an ntlm handshake at the url above
    resp2 = session.get(
        URL_NTLMTARGET,
        headers={
            'Referer': resp1.url  # pretend like this is a redirect
        },
        auth=requests_ntlm.HttpNtlmAuth(
            username, password
        )  # transaction credentials
    )

    if 'Daymap Identity Error' in resp2.text:
        raise ServerFault("daymap identity error in stage 2")

    if (rcode := resp2.status_code) != 200:
        raise InvalidCredentials(
            f"probably unauthorized, stage 2 code was {rcode}")

    if ('<form method="POST"' not in resp2.text):
        raise OurFault(
            f"weird return in stage 2, got code 200 but no form to post")
            
    # parse the html from stage 2's content
    s3_tree = lxml.html.fromstring(resp2.content)
    # get all inputs that aren't type submit
    inputs = s3_tree.xpath('//input[@type!="submit"]')
    # make a payload out of the inputs ready for sending
    post_payload = {inp.name: inp.value for inp in inputs}

    # send it to daymap's identity service
    resp3 = session.post(URL_DAYMAPIDENTITY, data=post_payload)

    if '<form' not in resp3.text:
        raise OurFault("weird return in stage 3, no form after post of stage 2 form")

    # parse the html from stage 3's content
    s4_tree = lxml.html.fromstring(resp3.content)
    # get all inputs
    inputs = s4_tree.xpath('//input')
    # make another payload from these inputs
    post_payload = {inp.name: inp.value for inp in inputs}

    # send it to /Daymap
    final = session.post(URL_SLASHDAYMAP, data=post_payload)
    if final.status_code != 200:
        raise OurFault(f"non 200 status code in final POST stage: {final.status_code}")

    if url == "":
        return final, session
    
    return session.get(url), session