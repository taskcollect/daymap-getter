from fastapi import APIRouter, Depends, HTTPException
from requests import Session
import datetime

from util.preprocess import prepare_auth_method, AuthModel, make_session_from_cookies, construct_response
from util.get.lessons import get_lessons
from util.errors import InvalidCredentials, ServerFault

import traceback


class LessonAndAuthModel(AuthModel):
    start: int
    end: int


def prepare_ranged_auth_methid(auth_and_range: LessonAndAuthModel):
    return prepare_auth_method(auth_and_range)


router = APIRouter(
    prefix='/lessons',
    dependencies=[Depends(prepare_ranged_auth_methid)]
)


@router.post("/")
def lesson_range(auth_and_range: LessonAndAuthModel):
    try:
        data, session = get_lessons(
            datetime.datetime.utcfromtimestamp(auth_and_range.start),
            datetime.datetime.utcfromtimestamp(auth_and_range.end),
            auth_and_range.username,
            auth_and_range.password,
            make_session_from_cookies(auth_and_range.cookies),
        )
    except InvalidCredentials:
        raise HTTPException(401, 'invalid credentials')
    except ServerFault as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        raise HTTPException(502, 'daymap is being weird')

    out = construct_response(
        data, auth_and_range.cookies,
        session.cookies.get_dict()
    )

    return out
