import asyncio
import datetime
import json
from aiohttp import web
import requests
import traceback
from daymap.errors import DaymapException

from daymap.util import get_all_lessons_and_clean


async def endpoint_lessons(req: web.Request) -> web.Response:

    start_date: datetime.datetime = None
    end_date: datetime.datetime = None

    username: str = None
    password: str = None

    cookies: str = None

    session: requests.Session = None

    try:
        data = await req.json()

        if type(data) != dict:
            raise "not a dict"

        data: dict

        start_date = datetime.datetime.utcfromtimestamp(
            int(data['from'])
        )

        end_date = datetime.datetime.utcfromtimestamp(
            int(data['to'])
        )

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
            raise "no password or cookies"

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return web.Response(status=400, text="invalid json")

    loop = asyncio.get_event_loop()

    def _get():
        return get_all_lessons_and_clean(
            start=start_date,
            end=end_date,
            username=username, 
            session=session, 
            password=password,
        )

    try:
        lessons, session = await loop.run_in_executor(None, _get)
    except Exception as e:
        if isinstance(e, DaymapException):
            return web.Response(status=int(e))

        # it's not a daymap parser error?
        traceback.print_exception(type(e), e, e.__traceback__)
        return web.Response(status=500)

    out = { "data": lessons }

    if cookies is None:
        # give back cookies if none received
        out["cookies"] = session.cookies.get_dict()

    body_out = json.dumps(out)
    return web.Response(body=body_out)
