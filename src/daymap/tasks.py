import datetime
from typing import Dict, List, Tuple

import lxml.html
import requests

import daymap.net

TASKS_URL = "https://daymap.gihs.sa.edu.au/daymap/student/portfolio.aspx/CurrentTaskList"


def parse_task_tr_grade_table(table: lxml.html.Element) -> dict:
    """
    Parse the grade table found in the task tr and return a dict.
    """
    grades = {}

    # there are a bunch of tr's in the table
    trs = table.xpath("tr")
    for tr in trs:
        # each tr contains two td's
        tds = tr.xpath("td")
        # the first td is a label, so let's use that as the key name
        k = tds[0].text_content().rstrip(":").lower()
        # the second td is the actual info, so let's use that as the value
        v = tds[1].xpath("div/text()")[0]
        # append that to the grade dict
        grades[k] = v

    return grades


def parse_task_tr(tr: lxml.html.Element) -> dict:
    """
    Parse a task table row into a dict.
    """

    tds = tr.xpath("td")

    # this contains whether the task is summative, what class it's for and what date it's due on
    # it's capped "cap_td" because it's a td element that has the class "cap" :)
    cap_td = tds[0]

    # get the div from the cap element with the class 'Caption'
    # this should be something like 'GIHS Summative'
    task_type = cap_td.xpath("div[@class='Caption']/text()")[0]

    if task_type == "GIHS Summative":
        task_type = "summative"
    elif task_type == "GIHS Formative":
        task_type = "formative"

    # now just parse the free floating text in the cap element, which happens to contain the things we need
    lesson_name, due_date_string = cap_td.xpath("text()")
    due_date = datetime.datetime.strptime(due_date_string, "%d/%m/%Y")

    # this is the second td that contains more useful data
    desc_td = tds[1]

    # this td has the property of having an onclick element that contains the task id
    # we can use this to get the task id - but it's in the form "return OpenTask(XXXXX);;"
    task_id = desc_td.get('onclick')[16:].split(')')[0]

    # this contains two divs, the first of which is the task title, the second is the due date
    desc_divs = desc_td.xpath("div")

    # this is the actual task title
    task_title = desc_divs[0].text_content().strip()

    # this is the due date & set on date
    # set_and_due_date = desc_divs[1].text_content().strip()

    alert_text = None
    grades = None
    if len(desc_divs) == 3:
        # this means that there's a third div, which yells at the student for
        # not submitting their work, eg. "Overdue. Work has not been received"
        # or simply "Work has not been received"
        alert_text = desc_divs[2].text_content().strip()
    else:
        # this means that the grade is actually out!
        # there should be a table here containing the grade results
        grade_table = desc_td.xpath("table")[0]
        grades = parse_task_tr_grade_table(grade_table)

    out = {
        "id": task_id,
        "title": task_title,
        "lessonName": lesson_name,
        "type": task_type,
        "dueDate": due_date.timestamp(),
    }

    # add this optional info if we got some
    if alert_text is not None and len(alert_text.strip()) > 0:
        out["alert"] = alert_text
    if grades is not None:
        out["grades"] = grades

    return out


def request_tasks_html(
    username: str,
    password: str = None,
    session: requests.Session = None
):
    r, s = daymap.net.request_daymap_resource(
        url=TASKS_URL,
        method="POST",
        username=username,
        password=password,
        session=session,
        payload="{classId: 0}",
        headers={
            "Content-Type": "application/json; charset=UTF-8"
        }
    )

    return r.json()['d'], s


def parse_tasks_html(html: str) -> List[Dict]:
    out = []

    table = lxml.html.fromstring(html)

    trs = table.xpath("tr")
    for tr in trs:
        tdclass = tr.xpath("td")[0].get('class')

        # there's a whole mix of tr's, but we only want the ones with a td inside
        # that have a class of "cap" (for god knows what reason)
        if tdclass == "cap":
            out.append(
                parse_task_tr(tr)
            )

    return out

def get_tasks(username: str, password: str = None, session: requests.Session = None) -> Tuple[List[dict], requests.Session]:
    html, session = request_tasks_html(
        username=username,
        password=password,
        session=session
    )

    return parse_tasks_html(html), session
