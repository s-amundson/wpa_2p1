from django.utils import timezone


def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the previous day
    (thus changing February 29 to March 1).
    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:  # pragma: no cover
        return add_years(d + timezone.timedelta(days=1), years)


def sub_years(d, years):
    """Return a date that's `years` years before the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).
    """
    try:
        return d.replace(year = d.year - years)
    except ValueError:  # pragma: no cover
        return sub_years(d + timezone.timedelta(days=1), years)
        # return d - (timezone.datetime(d.year - years, 1, 1) + timezone.datetime(d.year, 1, 1))
