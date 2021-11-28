import datetime
from typing import Dict, List, Tuple

import lxml.html
from requests.sessions import Session

# daymap modules
from ..net import request_daymap_resource

LESSON_URL = 'https://daymap.gihs.sa.edu.au/daymap/DWS/Diary.ashx?cmd=EventList&from={0}&to={1}'


def clean_daymap_date(d: str) -> datetime.datetime:
    # epic :10 gaming
    d = d.lstrip("/Date(").rstrip(")/").split("-")[0][:10]
    return datetime.datetime.utcfromtimestamp(float(d))

# convert the daymap given json to an actually good structure


def clean_lesson_object(l: dict) -> dict:
    return {
        "name": l["Title"].strip(),
        "id": l["ID"],
        "start": int(clean_daymap_date(l["Start"]).timestamp()),
        "finish": int(clean_daymap_date(l["Finish"]).timestamp()),
        "attendance": l["AttendanceStatus"],
    }


def get_lessons(
    start: datetime.date,
    end: datetime.date,
    username: str,
    password: str = None,
    session=None,
) -> Tuple[List[Dict], Session]:
    # construct url base
    url = LESSON_URL.format(
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d")
    )

    # request the url
    resp, session = request_daymap_resource(
        url=url,
        username=username,
        session=session,
        password=password,
    )  # (no need to try/except here, just let it raise naturally)

    rawlessons = resp.json()
    # process the lesson objects
    cleanlessons = [
        clean_lesson_object(l) for l in rawlessons
    ]

    return cleanlessons, session
