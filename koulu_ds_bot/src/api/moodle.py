import requests
import re
from bs4 import BeautifulSoup

def get_moodle_id(course_id):
    '''
        get course's id in moodle.

        course_id (str): ex. 90432Y
        returns 4 digit id for course ex. 5747 as string
    '''

    url = 'https://moodle.oulu.fi/search/index.php'
    req = requests.get(url, params = {'q': course_id})

    html = BeautifulSoup(req.content, 'html.parser')
    
    for result in html.find_all('div', {'class': 'result'}):
        result_course = result.find('div', {'class': 'result-content'}).contents[0]

        if course_id != result_course:
            continue

        moodle_url = result.find('a', href=True)['href']
        parsed_id = re.search('id=(\d+)', moodle_url).group(1)

        if parsed_id:
            return parsed_id

    return False


def get_calendar_dl_link(course_id):
    '''
        get link to download courses calendar from moodle.
        to download calendar you have to be logged in into moodle
        and also be enrolled to the course.
    '''
    base_url = 'https://moodle.oulu.fi/calendar/export.php?course='
    moodle_id = get_moodle_id(course_id)
    return base_url + moodle_id if moodle_id else False
