import time


def epoch_now():
    return int(gmt_plus_2(time.time()))


def remove_leading_digits_from_year(timestamp, delimiter):
    split_timestamp = timestamp.split(delimiter)
    if len(split_timestamp[-1]) == 4:
        year = split_timestamp[-1][2:]
        timestamp = delimiter.join(split_timestamp[:2] + [year])
    return timestamp


def timestamp_to_epoch(timestamp, delimiter):
    parsed_time = time.strptime(timestamp, f'%d{delimiter}%m{delimiter}%y')
    epoch_time = time.mktime(parsed_time)
    return int(epoch_time)


def gmt_plus_2(timestamp):
    two_hours_in_seconds = 7200
    summer_time_savings = 3600
    return timestamp + two_hours_in_seconds + summer_time_savings


def epoch_to_readable_date(epoch_time, exclude_year=False):
    if exclude_year:
        return time.strftime('%d.%m.', time.gmtime(int(float(epoch_time))))

    return time.strftime('%d.%m.%Y', time.gmtime(int(float(epoch_time))))


def epoch_to_readable_time(epoch_time):
    return time.strftime('%H:%M', time.gmtime(int(float(epoch_time))))


def current_hour():
    return int(time.strftime('%H', time.gmtime(epoch_now())))


def ics_format_to_epoch(ics_dt):
    # ex. "20210523T205900Z"
    year = ics_dt[2:4]
    month = ics_dt[4:6]
    day = ics_dt[6:8]

    return timestamp_to_epoch(f'{day}/{month}/{year}', '/')

def time_from_ics_stamp(ics_dt):
    # "20210523T205900Z" to "20:59"
    if ics_dt == 0:
        return None
    time_part = ics_dt.split('T')[1][:4]
    return time_part[:2] + ':' + time_part[2:]


def epoch_to_lecture_time(start_epoch, end_epoch):
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
