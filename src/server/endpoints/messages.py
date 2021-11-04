# HTTP endpoints for messages

import asyncio
import datetime
import json
import traceback

import requests
from aiohttp import web

from daymap.errors import DaymapException
import daymap.messages

# get the username and password from the request json, then query daymap, and return it as a json array
async def endpoint_messages(req: web.Request) -> web.Response:
    username: str = None
    password: str = None

    cookies: str = None

    session: requests.Session = None

    try:
        data = await req.json()

        if not isinstance(data, dict):
            raise ValueError("not a dict")

        data: dict

        username = data['username']
        password = data.get('password')

        cookies: dict or None = data.get("cookies")

        if cookies is not None:
            jar = requests.sessions.RequestsCookieJar()

            for cname, cvalue in cookies.items():
                jar.set(cname, cvalue)

            session = requests.Session()
            session.cookies = jar
        elif password is None:
            raise ValueError("no password or cookies")

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return web.Response(status=400, text="invalid json")

    loop = asyncio.get_event_loop()

    def _get():
        return daymap.messages.get_messages(username, password, session)

    try:
        lessons, session = await loop.run_in_executor(None, _get)
    except Exception as e:
        if isinstance(e, DaymapException):
            return web.Response(status=int(e))

        # it's not a daymap parser error?
        traceback.print_exception(type(e), e, e.__traceback__)
        return web.Response(status=500)

    out = {"data": lessons}

    # if no cookies were provided or the cookies were renewed, give them back
    if cookies is None or cookies != session.cookies:
        # give back cookies if none received
        out["cookies"] = session.cookies.get_dict()

    body_out = json.dumps(out)
    return web.Response(body=body_out)
