# -*- coding: utf-8 -*-
#==============================================================================
#
#       timefmt.py - Custom time formatting functions
#
#       2021-08-13 - Switch over to 'import timefmt as tmf'
#
#==============================================================================

from __future__ import print_function       # Must be first import
from __future__ import unicode_literals     # Unicode errors fix

import time
import datetime
from collections import namedtuple


def date_matrix(d=None, eow=5):
    """ Return named tuple with date attributes:
            we, wed, me, med, ye, yed
        From: https://stackoverflow.com/a/31997309/6929343
    """
    if d is None:
        d = datetime.date.today()

    # Last day of week:
    we = d + datetime.timedelta(days=eow - d.weekday())
    delta = we - d
    wed = delta.days

    # Last day of month:
    #me = datetime.date(year=(d.year + int(d.month % 12 == 0)),
    #    month=(d.month + 1) % 12, day=1) - datetime.timedelta(days=1)
    me = last_day_of_month(d)
    delta = me - d
    med = delta.days

    # Last day of quarter:
    # datetime.date(year=d.year, month=((d.month % 3) + 1) * 3 + 1, day=1) \
    #    - datetime.timedelta(days=1)
    # Last day of year:
    ye = datetime.date(year=d.year, month=12, day=31)
    delta = ye - d
    yed = delta.days

    Date = namedtuple('Date', 'this, we, wed, me, med, ye, yed')
    # noinspection PyArgumentList
    return Date(d, we, wed, me, med, ye, yed)


def last_day_of_month(d):
    """ From: https://stackoverflow.com/a/43088/6929343 """
    if d.month == 12:
        return d.replace(day=31)
    return d.replace(month=d.month+1, day=1) - datetime.timedelta(days=1)


def add_years(d, years):
    """ Add number of years to date, recognizing Feb 29
        From: https://stackoverflow.com/a/15743908/6929343

        Return a date that's `years` years after the date (or datetime)
        object `d`. Return the same calendar date (month and day) in the
        destination year, if it exists, otherwise use the following day
        (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (datetime.date(d.year + years, 3, 1) -
                    datetime.date(d.year, 3, 1))


def add_months(d, months):
    """ Add number of months to MONTH-END date
        From: https://stackoverflow.com/a/4131007/6929343
    """
    year, month = divmod(d.month + months + 1, 12)
    if month == 0:
        month = 12
        year = year - 1
    # First day of next month
    next_month = datetime.date(d.year + year, month, 1)
    # Subtract 1 day for last day of month
    return next_month - datetime.timedelta(days=1)


def get_sec(time_str):
    """Get Seconds from time: https://stackoverflow.com/a/6402859/6929343 """
    sections = time_str.count(':')
    # TODO: Support days in format 'd.hh:mm:ss'
    if sections == 0:
        h = m = 0  # No hours, no minutes
        s = time_str
    elif sections == 1:
        m, s = time_str.split(':')
        h = 0  # No hours
    else:
        h, m, s = time_str.split(':')  # Split "hh:mm:ss" into separate strings

    return int(h) * 3600 + int(m) * 60 + int(s)


def mm_ss(seconds, brackets=False, trim=True, rem=None):
    """ Convert seconds to minutes:seconds.decisecond
        decisecond is 1/10th of a second
        :param seconds is float
        :param brackets surround result in "[...]"
        :param trim suppresses minutes when 0
        :param rem = 'd' includes deci seconds, 'h' includes hundredths
    """
    i = int(seconds)
    d = seconds - i
    if d == 1.0:
        d = 0.0                             # Not working to strip out leading 1.?
    m, s = divmod(i, 60)
    result = ""
    ss = str(s)                             # ss is now seconds in string format

    if m > 0 or trim is False:
        result += str(m) + ":"              # minutes pass test
        if s < 10:
            ss = "0" + ss                   # Pad with leading zero

    result += ss                            # seconds are always present

    if rem == 'd':
        # decisecond is required # Not working to strip out leading 1.?
        result += str('%.1f' % d).lstrip('0').lstrip('1')
    elif rem == 'h':
        # hundredths is required # Not working to strip out leading 1.?
        result += str('%.2f' % d).lstrip('0').lstrip('1')

    if brackets is True:
        result = "[" + result + "]"         # Add brackets

    return result


# From mserve time_format() make it's own module called ??? (not time though)
# If MAX_DEPTH changes you must update 'depth_count = [ 0, 0, 0 ]' below.
LAST_WEEK = 60 * 60 * 24 * 7        # Formatted dates
LAST_YEAR = LAST_WEEK * 52          # Formatted dates


def ago(Time):
    """ Format time as 99 xx ago. """

    now = time.time()
    fmt_time = datetime.datetime.fromtimestamp(Time)

    ''' If < 12 hours ago use:  "hh:mm XM - 99 Hours ago"
        If < 1 week ago use:    "DayName - 9 Days ago"
        If < 1 year ago use:    "MonName DD - 9 Months ago"
        else use:               "MMM DD YYYY - 99 Years ago"
    '''
    difference = now - Time
    if difference < (12 * 60 * 60):             # Last 12 hours?
        fmt = fmt_time.strftime("%I:%M %p")       # Set HH:MM xm
        # Leading zero?
        if fmt.startswith("0"):                # HH: starts with 0?
            fmt = fmt.replace("0", "", 1)
        # How many minutes or hours ago?
        minutes = difference / 60
        if minutes < 1.0:
            fmt = fmt + " - Just now"
        elif minutes < 90.0:
            fmt = fmt + " - " + str(int(round(minutes))) + " Minutes ago"
        else:
            hours = difference / (60 * 60)
            fmt = fmt + " - " + str(int(round(hours))) + " Hours ago"

    elif difference < LAST_WEEK:                # Last 7 days?
        fmt = fmt_time.strftime("%A")        # Set day name
        # How many days ago?
        days = difference / (24 * 60 * 60)
        if days < 1.0:
            fmt = fmt + " - Yesterday"
        else:
            fmt = fmt + " - " + str(int(round(days))) + " Days ago"

    elif difference < LAST_YEAR:                # This year?
        fmt = fmt_time.strftime("%B %d")     # Set month name & day
        # How many weeks or months ago?
        weeks = difference / (7 * 24 * 60 * 60)
        if weeks < 1.5:
            fmt = fmt + " - Last week"
        elif weeks < 4.0:
            fmt = fmt + " - " + str(int(round(weeks))) + " Weeks ago"
        elif weeks < 6.0:
            fmt = fmt + " - Last month"
        else:
            months = difference / (30 * 24 * 60 * 60)
            fmt = fmt + " - " + str(int(round(months))) + " Months ago"
    else:                                       # Before this year
        fmt = fmt_time.strftime("%b %d %Y")       # Set Mon Day Year
        # How many years ago or last year?
        years = difference / (365 * 24 * 60 * 60)
        if years < 2.0:
            fmt = fmt + " - Last year"
        else:
            fmt = fmt + " - " + str(int(round(years))) + " Years ago"

    fmt = fmt.replace(" 0", " ", 1)           # "May 05" to "May 5"

    return fmt
