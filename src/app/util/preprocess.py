from fastapi import HTTPException
from pydantic import BaseModel

import requests


class AuthModel(BaseModel):
    username: str
    password: str = None
    cookies: dict = None


# preprocessors for fastapi http requests
def prepare_auth_method(auth: AuthModel):
    if auth.cookies is None and auth.password is None:
        raise HTTPException(401, "neither password nor cookies supplied")


def make_session_from_cookies(cookies: dict) -> requests.Session or None:
    if cookies is None:
        return None

    jar = requests.sessions.RequestsCookieJar()

    for cname, cvalue in cookies.items():
        jar.set(cname, cvalue)

    session = requests.Session()
    session.cookies = jar

    return session


def construct_response(data, cookies=None, out_cookies=None) -> dict:
    out = {
        'data': data
    }

    is_provided_empty = cookies is None or len(cookies) == 0

    if is_provided_empty or cookies != out_cookies:
        out['cookies'] = out_cookies

    return out
