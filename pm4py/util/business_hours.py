from datetime import datetime
from functools import lru_cache
from typing import List, Tuple

from pm4py.util import constants


_SECONDS_PER_DAY = 24 * 60 * 60


@lru_cache(maxsize=512)
def _prepare_business_hour_slots(business_hour_slots):
    """Normalize and precompute values for a weekly business schedule."""
    unified = []
    for begin, end in sorted(business_hour_slots):
        if unified and unified[-1][1] >= begin - 1:
            unified[-1][1] = max(unified[-1][1], end)
        else:
            unified.append([begin, end])

    slots = tuple((begin, end) for begin, end in unified)
    total_seconds = sum(end - start for start, end in slots)
    return slots, total_seconds


def _get_prepared_business_hour_slots(business_hour_slots):
    # Schedules are commonly passed as lists, so convert them to an immutable
    # value before looking them up in the cache. This also makes later changes
    # to a caller-owned list visible on the next calculation.
    slots = tuple((begin, end) for begin, end in business_hour_slots)
    return _prepare_business_hour_slots(slots)


def _seconds_from_week_start(dt):
    """Return wall-clock seconds since Monday 00:00 without temporaries."""
    return (
        dt.weekday() * _SECONDS_PER_DAY
        + dt.hour * 60 * 60
        + dt.minute * 60
        + dt.second
        + dt.microsecond / 1000000
    )


def _business_seconds_from_week_start(dt, business_hour_slots):
    seconds_since_week_start = _seconds_from_week_start(dt)
    total = 0.0
    for start, end in business_hour_slots:
        if seconds_since_week_start <= start:
            break
        total += max(0, min(seconds_since_week_start, end) - start)
    return total


def _get_business_seconds(
    datetime1, datetime2, business_hour_slots, total_seconds_per_week
):
    if datetime2 <= datetime1:
        return 0.0

    # Subtracting the weekday from the ordinal gives the Monday ordinal for
    # each timestamp, avoiding date, datetime, and timedelta allocations.
    week_start1 = datetime1.toordinal() - datetime1.weekday()
    week_start2 = datetime2.toordinal() - datetime2.weekday()
    number_of_weeks = (week_start2 - week_start1) // 7

    seconds1 = _business_seconds_from_week_start(
        datetime1, business_hour_slots
    )
    seconds2 = _business_seconds_from_week_start(
        datetime2, business_hour_slots
    )
    return (
        total_seconds_per_week * number_of_weeks + seconds2 - seconds1
    )


class BusinessHours:
    def __init__(self, datetime1, datetime2, **kwargs):
        # Remove timezone info for simplicity (assumes same timezone)
        self.datetime1 = (
            datetime1.replace(tzinfo=None)
            if datetime1.tzinfo is not None
            else datetime1
        )
        self.datetime2 = (
            datetime2.replace(tzinfo=None)
            if datetime2.tzinfo is not None
            else datetime2
        )
        # Use provided business hour slots or default
        self.business_hour_slots = (
            kwargs["business_hour_slots"]
            if "business_hour_slots" in kwargs
            else constants.DEFAULT_BUSINESS_HOUR_SLOTS
        )
        # Unify slots to avoid overlaps
        unified_slots, _ = _get_prepared_business_hour_slots(
            self.business_hour_slots
        )
        # Keep the existing mutable representation of this attribute for
        # compatibility.
        self.business_hour_slots_unified = [
            list(slot) for slot in unified_slots
        ]
        # Work calendar (unused in this implementation)
        self.work_calendar = (
            kwargs["work_calendar"]
            if "work_calendar" in kwargs
            else constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR
        )

    def business_seconds_from_week_start(self, dt):
        """Calculate business seconds from the week start to ``dt``."""
        return _business_seconds_from_week_start(
            dt, self.business_hour_slots_unified
        )

    def get_seconds(self):
        """Calculate total business seconds between datetime1 and datetime2."""
        total_seconds_per_week = sum(
            end - start
            for start, end in self.business_hour_slots_unified
        )
        return _get_business_seconds(
            self.datetime1,
            self.datetime2,
            self.business_hour_slots_unified,
            total_seconds_per_week,
        )


def soj_time_business_hours_diff(
    st: datetime,
    et: datetime,
    business_hour_slots: List[Tuple[int]],
    work_calendar=constants.DEFAULT_BUSINESS_HOURS_WORKCALENDAR,
) -> float:
    """
    Calculates the difference between the provided timestamps based on business hours.

    Parameters
    ----------
    st : datetime
        Start timestamp
    et : datetime
        End timestamp
    business_hour_slots : List[Tuple[int]]
        Work schedule as list of tuples (start, end) in seconds since week start
    work_calendar
        Work calendar (unused in this implementation)

    Returns
    -------
    float
        Difference in business hours (seconds)
    """
    if st.tzinfo is not None:
        st = st.replace(tzinfo=None)
    if et.tzinfo is not None:
        et = et.replace(tzinfo=None)
    slots, total_seconds_per_week = _get_prepared_business_hour_slots(
        business_hour_slots
    )
    return _get_business_seconds(st, et, slots, total_seconds_per_week)
