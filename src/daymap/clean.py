import datetime
from typing import List

import lxml.html

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
        plan_id, event_id = a.attrib['href'].lstrip("javascript:planOpen(").rstrip(");").split(",")
        out.append({
            "label": a.text,
            "planId": int(plan_id),
            "eventId": int(event_id)
        })
    return out
