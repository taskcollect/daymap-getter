from fastapi import APIRouter, Depends, HTTPException
from requests import Session
import datetime
from util.get.lesson_plans import get_lesson_plans

from util.preprocess import prepare_auth_method, AuthModel, make_session_from_cookies, construct_response
from util.get.lessons import get_lessons
from util.errors import InvalidCredentials, ServerFault

import traceback


class TimeRangeAuthModel(AuthModel):
    start: int
    end: int


def prepare_ranged_authmodel(model: TimeRangeAuthModel):
    return prepare_auth_method(model)


router = APIRouter(
    prefix='/lessons',
)


@router.post("/", dependencies=[Depends(prepare_ranged_authmodel)])
def lesson_range(model: TimeRangeAuthModel):
    try:
        data, session = get_lessons(
            datetime.datetime.utcfromtimestamp(model.start),
            datetime.datetime.utcfromtimestamp(model.end),
            model.username,
            model.password,
            make_session_from_cookies(model.cookies),
        )
    except InvalidCredentials:
        raise HTTPException(401, 'invalid credentials')
    except ServerFault as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        raise HTTPException(502, 'daymap is being weird')

    out = construct_response(
        data, model.cookies,
        session.cookies.get_dict()
    )

    return out


class LessonIDAuthModel(AuthModel):
    lesson_id: int


def prepare_lid_authmodel(model: LessonIDAuthModel):
    return prepare_auth_method(model)


@router.post("/plans", dependencies=[Depends(prepare_lid_authmodel)])
def lesson_details(model: LessonIDAuthModel):
    try:
        notes, extra_files, session = get_lesson_plans(
            model.lesson_id,
            model.username,
            model.password,
            make_session_from_cookies(model.cookies),
        )

        data = {
            'notes': notes,
        }
        if extra_files:
            data['extra_files'] = extra_files

    except InvalidCredentials:
        raise HTTPException(401, 'invalid credentials')
    except ServerFault as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        raise HTTPException(502, 'daymap is being weird')

    out = construct_response(
        data, model.cookies,
        session.cookies.get_dict()
    )

    return out
