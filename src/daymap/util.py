import datetime
from typing import Dict, List, Tuple

from requests.sessions import Session

import daymap.clean
# daymap modules
import daymap.net

LESSON_URL = 'https://daymap.gihs.sa.edu.au/daymap/DWS/Diary.ashx?cmd=EventList&from={0}&to={1}'

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
    resp, session = daymap.net.get_daymap_resource(
        url=url,
        username=username,
        session=session,
        password=password,
    ) # (no need to try/except here, just let it raise naturally)

    rawlessons = resp.json()
    # process the lesson objects
    cleanlessons = [
        daymap.clean.clean_lesson_object(l) for l in rawlessons
    ]

    return cleanlessons, session
