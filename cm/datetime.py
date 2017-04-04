from mx import DateTime
import time
from cm import config


WIDGET_DATE_FMT = config.DATE_FORMAT[0]
WIDGET_TIME_FMT = config.TIME_FORMAT[0]
WIDGET_DATETIME_FMT = config.DATETIME_FORMAT[0]

PY_DATE_FMT = config.DATE_FORMAT[1]
PY_TIME_FMT = config.TIME_FORMAT[1]
PY_DATETIME_FMT = config.DATETIME_FORMAT[1]

PG_DATE_FMT = config.DATE_FORMAT[2]
PG_TIME_FMT = config.TIME_FORMAT[2]
PG_DATETIME_FMT = config.DATETIME_FORMAT[2]


def validate(string, format):
    time.strptime(string, format)


def now():
    """Returns a string of the current time in the determined format."""
    return time.strftime(PY_DATETIME_FMT)

def format(dt):
    """Returns a string of datetime in the determined format.
    This function is usually called to format the datetime value
    returned from the database.
    
    dt -- mx.DateTime object.
    """
    return dt.strftime(PY_DATETIME_FMT)


