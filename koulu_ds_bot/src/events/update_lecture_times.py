from ..api.peppi import get_course_info
from .uusikurssi import parse_lecture_times


def get_updated_lectures(peppi_id):
    '''
        peppi_id (str): "903213Y"
        Get lecture times for given peppi_id
    '''
    
    try:
        updated_info = get_course_info(peppi_id)
    except IndexError:
        # Course not available anymore
        return None

    return parse_lecture_times(updated_info)
