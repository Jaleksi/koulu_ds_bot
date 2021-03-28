from icalendar import Calendar, Event
from .time_utils import ics_format_to_epoch, epoch_now, time_from_ics_stamp

def parse_events_from_ics(ics_contents):
    parsed_events = []
    cal = Calendar.from_ical(ics_contents)
    now = epoch_now()
    for item in cal.walk():
        if item.name == 'VEVENT':
            category = item.get('categories').to_ical().decode('utf-8')
            summary = item.get('summary').to_ical().decode('utf-8')
            timestamp = item.get('dtend', 0).to_ical().decode('utf-8')
            summary += f' ({time_from_ics_stamp(timestamp)})'
            timestamp = ics_format_to_epoch(timestamp)

            if timestamp < now:
                continue

            parsed_events.append({
                'category': ''.join(category),
                'timestamp': timestamp,
                'msg': summary
            })

    return parsed_events
