from typing import Union
import time


def epoch_now() -> int:
    return int(gmt_plus_2(time.time()))


def remove_leading_digits_from_year(timestamp: str, delimiter: str) -> str:
    split_timestamp = timestamp.split(delimiter)
    if len(split_timestamp[-1]) == 4:
        year = split_timestamp[-1][2:]
        timestamp = delimiter.join(split_timestamp[:2] + [year])
    return timestamp


def timestamp_to_epoch(timestamp: str, delimiter: str) -> int:
    parsed_time = time.strptime(timestamp, f'%d{delimiter}%m{delimiter}%y')
    epoch_time = time.mktime(parsed_time)
    return int(epoch_time)


def gmt_plus_2(timestamp: int) -> int:
    two_hours_in_seconds = 7200
    summer_time_savings = 3600
    return timestamp + two_hours_in_seconds + summer_time_savings


def epoch_to_readable_date(epoch_time: Union[int, str],
                           exclude_year: bool = False
                           ) -> str:
    if exclude_year:
        return time.strftime('%d.%m.', time.gmtime(int(float(epoch_time))))

    return time.strftime('%d.%m.%Y', time.gmtime(int(float(epoch_time))))


def epoch_to_readable_time(epoch_time: Union[str, int]) -> str:
    return time.strftime('%H:%M', time.gmtime(int(float(epoch_time))))


def current_hour() -> int:
    return int(time.strftime('%H', time.gmtime(epoch_now())))


def ics_format_to_epoch(ics_dt: str) -> int:
    # ex. "20210523T205900Z"
    year = ics_dt[2:4]
    month = ics_dt[4:6]
    day = ics_dt[6:8]

    return timestamp_to_epoch(f'{day}/{month}/{year}', '/')

def time_from_ics_stamp(ics_dt: str) -> Union[str, None]:
    # "20210523T205900Z" to "20:59"
    if ics_dt == 0:
        return None
    time_part = ics_dt.split('T')[1][:4]
    hours = int(time_part[:2])
    timezone_add = 3

    if hours + timezone_add >= 24:
        hours = hours + timezone_add - 24
    else:
        hours += timezone_add

    mins = time_part[2:]
    return f'{hours}:{mins}'


def epoch_to_lecture_time(start_epoch: Union[int, str],
                          end_epoch: Union[int, str]
                          ) -> str:
    # return format "Ma 19.2. 14:00-16:00"
    weekdays_fi = {
        'Mon': 'Ma',
        'Tue': 'Ti',
        'Wed': 'Ke',
        'Thu': 'To',
        'Fri': 'Pe',
        'Sat': 'La',
        'Sun': 'Su'
    }
    wkday = weekdays_fi[time.strftime('%a', time.gmtime(int(start_epoch)))]
    start_time = epoch_to_readable_time(start_epoch)
    end_time = epoch_to_readable_time(end_epoch)
    date = epoch_to_readable_date(start_epoch, True)

    return f'{wkday} {date} {start_time}-{end_time}'
