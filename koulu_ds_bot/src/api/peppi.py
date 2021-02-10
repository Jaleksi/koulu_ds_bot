import requests

def get_course_info(course_id=None, education_id=None):
    '''
        course_id (str) : public id for course eg. "902145Y"
        education_id (str) : course id in peppi eg. "6165"
    '''

    if education_id is None:
        content = requests.get(f'https://opasbe.peppi.oulu.fi/api/lu/units/{course_id}/COURSE_UNIT').json()
        education_id = content['learningUnits'][0]['learningUnitId']

    req_url = f'https://opasbe.peppi.oulu.fi/api/realizations/course/{education_id}'
    course_info = requests.get(req_url).json()[0]
    return course_info
