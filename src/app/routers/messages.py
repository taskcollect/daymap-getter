from fastapi import APIRouter, Depends, HTTPException
from requests import Session

from util.preprocess import prepare_auth_method, AuthModel, make_session_from_cookies, construct_response
from util.get.messages import get_messages
from util.errors import InvalidCredentials, ServerFault

import traceback

router = APIRouter(
    prefix='/messages',
    dependencies=[Depends(prepare_auth_method)]
)


@router.post("/")
def all_messages(auth: AuthModel):
    try:
        data, session = get_messages(
            auth.username,
            auth.password,
            make_session_from_cookies(auth.cookies)
        )
    except InvalidCredentials:
        raise HTTPException(401, 'invalid credentials')
    except ServerFault as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        raise HTTPException(502, 'daymap is being weird')

    out = construct_response(
        data, auth.cookies,
        session.cookies.get_dict()
    )

    return out
