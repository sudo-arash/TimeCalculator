"""Core value types and arithmetic helpers for the calculator."""

import calendar
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Union

EPSILON = 1e-10


class CalcError(ValueError):
    """An expected, user-facing calculator error."""


@dataclass
class Number:
    """A normal numeric value."""

    value: float


@dataclass
class Span:
    """A duration such as 2h 30m or 3d."""

    years: float = 0.0
    months: float = 0.0
    weeks: float = 0.0
    days: float = 0.0
    hours: float = 0.0
    minutes: float = 0.0
    seconds: float = 0.0


@dataclass
class Clock:
    """A time-of-day-style value, represented internally as seconds."""

    seconds: float


@dataclass
class Point:
    """A calendar date or date-time."""

    value: datetime
    is_date: bool


Value = Union[Number, Span, Clock, Point]


def clean(value):
    """Remove insignificant floating-point noise in O(1)."""
    if abs(value) < EPSILON:
        return 0.0
    if abs(value - round(value)) < EPSILON:
        return float(round(value))
    return value


def normalize_span(span):
    """Normalize a duration in O(1).

    Weeks become days; seconds/minutes/hours carry upward.
    Months carry into years. Months and years are never converted
    into days because calendar month/year lengths vary.
    """
    years = span.years
    months = span.months
    days = span.days + span.weeks * 7.0
    hours = span.hours
    minutes = span.minutes
    seconds = span.seconds

    carry = math.trunc(months / 12.0)
    years += carry
    months -= carry * 12.0

    carry = math.trunc(seconds / 60.0)
    minutes += carry
    seconds -= carry * 60.0

    carry = math.trunc(minutes / 60.0)
    hours += carry
    minutes -= carry * 60.0

    carry = math.trunc(hours / 24.0)
    days += carry
    hours -= carry * 24.0

    fixed_seconds = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds

    if abs(fixed_seconds) < EPSILON:
        days = hours = minutes = seconds = 0.0
    else:
        sign = -1.0 if fixed_seconds < 0 else 1.0
        magnitude = abs(fixed_seconds)

        days = int(magnitude // 86400.0)
        magnitude %= 86400.0
        hours = int(magnitude // 3600.0)
        magnitude %= 3600.0
        minutes = int(magnitude // 60.0)
        seconds = magnitude % 60.0

        days *= sign
        hours *= sign
        minutes *= sign
        seconds *= sign

    return Span(
        years=clean(years),
        months=clean(months),
        days=clean(days),
        hours=clean(hours),
        minutes=clean(minutes),
        seconds=clean(seconds),
    )


def add_span(left, right):
    """Add durations in O(1)."""
    return normalize_span(
        Span(
            years=left.years + right.years,
            months=left.months + right.months,
            days=left.days + right.days,
            hours=left.hours + right.hours,
            minutes=left.minutes + right.minutes,
            seconds=left.seconds + right.seconds,
        )
    )


def subtract_span(left, right):
    """Subtract durations in O(1)."""
    return add_span(left, negate(right))


def scale_span(span, factor):
    """Multiply a duration by a scalar in O(1)."""
    years = span.years * factor
    months = span.months * factor

    if span.years and abs(years - round(years)) > EPSILON:
        raise CalcError("Years must remain whole when scaled.")
    if span.months and abs(months - round(months)) > EPSILON:
        raise CalcError("Months must remain whole when scaled.")

    return normalize_span(
        Span(
            years=years,
            months=months,
            days=span.days * factor,
            hours=span.hours * factor,
            minutes=span.minutes * factor,
            seconds=span.seconds * factor,
        )
    )


def span_seconds(span):
    """Convert a fixed duration to seconds in O(1)."""
    if abs(span.years) > EPSILON or abs(span.months) > EPSILON:
        raise CalcError("Months and years do not have a fixed number of seconds.")

    return (
        span.days * 86400.0
        + span.hours * 3600.0
        + span.minutes * 60.0
        + span.seconds
    )


def negate(value):
    """Negate a scalar, duration, or clock value in O(1)."""
    if isinstance(value, Number):
        return Number(-value.value)
    if isinstance(value, Span):
        return normalize_span(
            Span(
                years=-value.years,
                months=-value.months,
                days=-value.days,
                hours=-value.hours,
                minutes=-value.minutes,
                seconds=-value.seconds,
            )
        )
    if isinstance(value, Clock):
        return Clock(-value.seconds)
    raise CalcError("A date cannot be negative.")


def shift_datetime(base, span):
    """Apply a calendar-aware duration to a datetime in O(1)."""
    if abs(span.years - round(span.years)) > EPSILON:
        raise CalcError("Years must be whole numbers.")
    if abs(span.months - round(span.months)) > EPSILON:
        raise CalcError("Months must be whole numbers.")

    total_months = int(round(span.years)) * 12 + int(round(span.months))
    result = base

    if total_months:
        index = result.year * 12 + result.month - 1 + total_months
        year, month_index = divmod(index, 12)
        month = month_index + 1
        day = min(result.day, calendar.monthrange(year, month)[1])
        result = result.replace(year=year, month=month, day=day)

    return result + timedelta(
        days=span.days + span.weeks * 7.0,
        hours=span.hours,
        minutes=span.minutes,
        seconds=span.seconds,
    )
