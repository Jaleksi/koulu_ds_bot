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
    return timestamp + two_hours_in_seconds


def epoch_to_readable_date(epoch_time):
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
