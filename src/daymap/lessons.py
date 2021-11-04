import lxml.html
from typing import List
import datetime
from typing import Dict, List, Tuple

from requests.sessions import Session

# daymap modules
import daymap.net

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
        "resources": l["HasResources"],
        "links": (get_links_from_planopen(l["Text"]) if l["Text"] != "" else None)
    }


def get_links_from_planopen(s: str) -> List[dict]:
    tree = lxml.html.fromstring(s)
    # get all inputs
    anchors: List[lxml.html.HtmlElement] = tree.xpath('//a')

    out = []
    for a in anchors:
        plan_id, event_id = a.attrib['href'].lstrip(
            "javascript:planOpen(").rstrip(");").split(",")
        out.append({
            "label": a.text,
            "planId": int(plan_id),
            "eventId": int(event_id)
        })
    return out


def get_all_lessons_and_clean(
    start: datetime.date,
    end: datetime.date,
    username: str,
    session=None,
    password: str = None
) -> Tuple[List[Dict], Session]:
    # construct url base
    url = LESSON_URL.format(
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d")
    )

    # request the url
    resp, session = daymap.net.request_daymap_resource(
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
