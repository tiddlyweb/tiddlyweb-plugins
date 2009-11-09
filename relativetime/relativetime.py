
from datetime import datetime, timedelta

from tiddlyweb.filters import FilterError
from tiddlyweb.filters.sort import ATTRIBUTE_SORT_KEY, date_to_canonical

def init(config):
    pass


def parse_date(datestring):
    """
    We expect either a tiddlywiki timestamp string,
    a fragment thereof, or some numbers that end with
    'd', 's', 'm', 'h', 'y' (case insensitive) meaning
    Days, Seconds, Minutes, Hours, Years. We don't worry
    about months. If the trailing letter is there, we
    translate it into an absolute time in the past, relative
    to now.
    """
    end = datestring[-1].lower()
    if not end.isdigit():
        datestring = _parse_relative_time(datestring)
    return date_to_canonical(datestring)


def _parse_relative_time(datestring):
    time_type = datestring[-1]
    time_value = int(datestring[0:-1])
    # clearly this can be cleared up
    if time_type == 'y':
        time_type = 'd'
        time_value = time_value * 365
    if time_type == 'd':
        delta = timedelta(days=time_value)
    elif time_type == 's':
        delta = timedelta(seconds=time_value)
    elif time_type == 'm':
        delta = timedelta(minutes=time_value)
    elif time_type == 'h':
        delta = timedelta(hours=time_value)
    else:
        raise FilterError('unknown time type in filter')
    time_object = datetime.utcnow() - delta
    datestring = unicode(time_object.strftime('%Y%m%d%H%M%S'))
    print 'datestring is', datestring
    return datestring


# reset ATTRIBUTE_SORT_KEY to local func
ATTRIBUTE_SORT_KEY.update({'modified': parse_date, 'created': parse_date})

if __name__ == '__main__':
    print parse_date('2009')
    print parse_date('1d')
    print parse_date('1h')
    print parse_date('1m')
    print parse_date('1s')
    print parse_date('1y')
    print parse_date('1x')

