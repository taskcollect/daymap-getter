from fastapi import APIRouter, Depends, HTTPException
from requests import Session


from util.preprocess import prepare_auth_method, AuthModel, make_session_from_cookies, construct_response
from util.get.tasks import get_tasks
from util.errors import InvalidCredentials, OurFault, ServerFault

import traceback

router = APIRouter(
    prefix='/tasks',
    dependencies=[Depends(prepare_auth_method)]
)


@router.post("/")
def all_current_tasks(auth: AuthModel):
    try:
        data, session = get_tasks(
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
