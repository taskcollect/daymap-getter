from typing import List, Tuple
import requests
import daymap.net
import lxml.html

MESSAGES_URL = "https://daymap.gihs.sa.edu.au/daymap/coms/search.aspx/Search"

def request_message_html(
    username: str,
    password: str = None,
    session: requests.Session = None
):
    r, s = daymap.net.request_daymap_resource(
        url=MESSAGES_URL,
        method="POST",
        username=username,
        password=password,
        session=session,
        payload='{"via": 0, "keyword": "", "dateRange": "Anytime"}',
        headers={
            "Content-Type": "application/json; charset=UTF-8"
        }
    )
    
    return r.json()['d'], s


def parse_message_html(html: str):
    tree = lxml.html.fromstring(html)
    messageDivs = tree.xpath("/html/body/div/div[2]/div[@id]")

    messages = []

    for div in messageDivs:
        # the div's id is in the format "message|XXXXXX", so let's just get the number
        id = div.get("id").split("|")[-1]
        rows = div.xpath("table/tr")

        # parse the first row, which contains the sender and date
        sender = rows[0].xpath("td[2]/text()")[0]
        date = rows[0].xpath("td[3]/text()")[0]

        # parse the second row, which contains the subject
        subject = " ".join(rows[1].xpath("td[1]/text()"))

        messages.append({
            "id": id,
            "sender": sender,
            "date": date,
            "subject": subject
        })

    return messages


def get_messages(username: str, password: str = None, session: requests.Session = None) -> Tuple[List[dict], requests.Session]:
    html, session = request_message_html(
        username=username,
        password=password,
        session=session
    )

    return parse_message_html(html), session
