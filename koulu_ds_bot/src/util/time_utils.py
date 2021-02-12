import time


def epoch_now():
    return int(time.time())


def remove_leading_digits_from_year(timestamp, delimiter):
    split_timestamp = timestamp.split(delimiter)
    if len(split_timestamp[-1]) == 4:
        year = split_timestamp[-1][2:]
        timestamp = delimiter.join(split_timestamp[:2] + [year])
    return timestamp


def timestamp_to_epoch(timestamp, delimiter):
    parsed_time = time.strptime(timestamp, f'%d{delimiter}%m{delimiter}%y')
    epoch_time = time.mktime(parsed_time)
    return epoch_time


def epoch_to_readable(epoch_time):
    return time.strftime('%d.%m.%Y', time.gmtime(int(float(epoch_time))))


def current_hour():
    return time.strftime('%H', time.gmtime(epoch_now()))
