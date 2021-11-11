# HTTP endpoints for tasks

import traceback
import requests

from flask import request, jsonify, Blueprint

from daymap.errors import DaymapException
import daymap.tasks
from util import preprocess_json

blueprint = Blueprint("tasks", __name__)


@blueprint.route('/tasks', methods=['GET'])
async def endpoint_tasks_current():
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
        tasks, session = daymap.tasks.get_tasks(username, password, session)
    except Exception as e:
        if isinstance(e, DaymapException):
            return '', int(e)

        # it's not a daymap parser error?
        traceback.print_exception(type(e), e, e.__traceback__)
        return '', 500

    out = {"data": tasks}

    # if no cookies were provided or the cookies were renewed, give them back
    if cookies is None or cookies != session.cookies:
        # give back cookies if none received
        out["cookies"] = session.cookies.get_dict()

    return jsonify(out)
