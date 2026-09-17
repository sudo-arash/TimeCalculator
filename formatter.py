"""Result formatting. All formatters operate in O(1)."""

from values import EPSILON, Clock, Number, Point, Span, span_seconds


def format_number(value):
    if abs(value) < EPSILON:
        return "0"
    if abs(value - round(value)) < EPSILON:
        return str(int(round(value)))
    return "{:.10f}".format(value).rstrip("0").rstrip(".")


def format_clock(seconds):
    sign = "-" if seconds < 0 else ""
    seconds = abs(seconds)

    days = int(seconds // 86400)
    seconds %= 86400
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60

    if abs(seconds - round(seconds)) < EPSILON:
        sec = "{:02d}".format(int(round(seconds)))
    else:
        sec = "{:05.2f}".format(seconds)

    result = "{:02d}:{:02d}:{}".format(hours, minutes, sec)
    return sign + ("{}d ".format(days) if days else "") + result


def format_span_words(span):
    if abs(span.years) < EPSILON and abs(span.months) < EPSILON:
        total = span_seconds(span)
        if abs(total) < EPSILON:
            return "0 seconds"

        sign = "-" if total < 0 else ""
        magnitude = abs(total)
        days = int(magnitude // 86400)
        magnitude %= 86400
        hours = int(magnitude // 3600)
        magnitude %= 3600
        minutes = int(magnitude // 60)
        seconds = magnitude % 60

        parts = []
        if days: parts.append("{} {}".format(days, "day" if days == 1 else "days"))
        if hours: parts.append("{} {}".format(hours, "hour" if hours == 1 else "hours"))
        if minutes: parts.append("{} {}".format(minutes, "minute" if minutes == 1 else "minutes"))
        if seconds > EPSILON:
            parts.append("{} {}".format(
                format_number(seconds),
                "second" if abs(seconds - 1) < EPSILON else "seconds"
            ))
        return sign + " ".join(parts)

    parts = []
    for label, amount in (
        ("year", span.years),
        ("month", span.months),
        ("day", span.days),
        ("hour", span.hours),
        ("minute", span.minutes),
        ("second", span.seconds),
    ):
        if abs(amount) < EPSILON:
            continue
        magnitude = abs(amount)
        plural = label if abs(magnitude - 1) < EPSILON else label + "s"
        parts.append("{}{} {}".format(
            "-" if amount < 0 else "",
            format_number(magnitude),
            plural,
        ))
    return " ".join(parts) or "0 seconds"


def format_result(value):
    """Return (display, type, explanation)."""
    if isinstance(value, Number):
        return format_number(value.value), "Number", "Normal arithmetic"

    if isinstance(value, Clock):
        return format_clock(value.seconds), "Time", "Time arithmetic"

    if isinstance(value, Span):
        return format_span_words(value), "Duration", "Duration arithmetic"

    if isinstance(value, Point):
        if value.is_date:
            return value.value.strftime("%d/%m/%Y"), "Date", "Calendar arithmetic"
        return value.value.strftime("%d/%m/%Y %H:%M:%S"), "Date & time", "Calendar arithmetic"

    raise ValueError("Unsupported value.")
