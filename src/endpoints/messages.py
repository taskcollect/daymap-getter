# HTTP endpoints for messages

import traceback

from flask import request, jsonify, Blueprint

import requests

from daymap.errors import DaymapException
import daymap.messages
from util import preprocess_json

blueprint = Blueprint("messages", __name__)


@blueprint.route('/messages', methods=['GET'])
def endpoint_messages():
    username: str = None
    password: str = None

    cookies: str = None

    session: requests.Session = None

    try:
        data = preprocess_json(request.data.decode('utf-8'))

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
        return "invalid json", 400

    try:
        lessons, session = daymap.messages.get_messages(
            username, password, session)
    except Exception as e:
        if isinstance(e, DaymapException):
            return '', int(e)

        # it's not a daymap parser error?
        traceback.print_exception(type(e), e, e.__traceback__)
        return '', 500

    out = {"data": lessons}

    # if no cookies were provided or the cookies were renewed, give them back
    if cookies is None or cookies != session.cookies:
        # give back cookies if none received
        out["cookies"] = session.cookies.get_dict()

    return jsonify(out)
