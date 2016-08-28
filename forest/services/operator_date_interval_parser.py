import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

PERIODS = [
    'yesterday',
    'lastWeek',
    'last2Weeks',
    'lastMonth',
    'last3Months',
    'lastYear'
]

PERIODS_VALUES = {
    'days': 'day',
    'weeks': 'isoWeek',
    'months': 'month',
    'years': 'year'
}

PERIOD_LAST_X_DAYS_REGEX = re.compile(r'^last(\d+)days$')

def is_interval_date_value(value):
    if value in PERIODS:
        return True

    match = PERIOD_LAST_X_DAYS_REGEX.match(value)
    if match:
        return True

    return False

def reset_time(date):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)

def get_interval_date_filter(value):
    if not is_interval_date_value(value):
        return

    now = datetime.utcnow()

    match = PERIOD_LAST_X_DAYS_REGEX.match(value)
    if match:
        start = now - timedelta(days=match.group(1))
        return (start,)

    start = end = None

    if value == 'yesterday':
        start = now - timedelta(days=1)
        start = reset_time(start)
        end = now
        end = reset_time(end)

    elif value == 'lastWeek':
        start = now - timedelta(weeks=1)
        start = start - timedelta(days=start.weekday())
        start = reset_time(start)
        end = now - timedelta(days=6-now.weekday())
        end = reset_time(end)

    elif value == 'last2Weeks':
        start = now - timedelta(weeks=2)
        start = start - timedelta(days=start.weekday())
        start = reset_time(start)
        end = now - timedelta(days=6-now.weekday())
        end = reset_time(end)

    elif value == 'lastMonth':
        start = now - relativedelta(months=1)
        start = start.replace(start.year, start.month, 1)
        start = reset_time(start)
        end = now.replace(now.year, now.month, 1)
        end = reset_time(end)

    elif value == 'last3Month':
        start = now - relativedelta(months=3)
        start = start.replace(start.year, start.month, 1)
        start = reset_time(start)
        end = now.replace(now.year, now.month, 1)
        end = reset_time(end)

    elif value == 'lastYear':
        start = now - relativedelta(years=1)
        start = start.replace(start.year, 1, 1)
        start = reset_time(start)
        end = now.replace(now.year, 1, 1)
        end = reset_time(end)

    return (start, end)

