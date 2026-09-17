"""Recursive-descent parser and arithmetic dispatch."""

from datetime import datetime
from typing import List, Optional

from lexer import DURATION_RE, DATE_RE, TIME_RE, Token, tokenize
from values import (
    CalcError,
    Clock,
    Number,
    Point,
    Span,
    Value,
    add_span,
    negate,
    scale_span,
    shift_datetime,
    span_seconds,
    subtract_span,
    normalize_span,
)

UNIT_ALIASES = {
    "y": "years", "yr": "years", "yrs": "years", "year": "years", "years": "years",
    "mo": "months", "mon": "months", "mons": "months", "month": "months", "months": "months",
    "w": "weeks", "wk": "weeks", "week": "weeks", "weeks": "weeks",
    "d": "days", "day": "days", "days": "days",
    "h": "hours", "hr": "hours", "hrs": "hours", "hour": "hours", "hours": "hours",
    "m": "minutes", "min": "minutes", "mins": "minutes", "minute": "minutes", "minutes": "minutes",
    "s": "seconds", "sec": "seconds", "secs": "seconds", "second": "seconds", "seconds": "seconds",
}


class Parser:
    """Parse calculator expressions in O(n)."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[Token]:
        """Look at the current token without consuming it."""
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def consume(self) -> Token:
        """Consume one token; never returns None."""
        token = self.peek()
        if token is None:
            raise CalcError("The expression ends too early.")
        self.pos += 1
        return token

    def parse(self) -> Value:
        if not self.tokens:
            raise CalcError("Enter something to calculate.")

        result = self.parse_expression()
        extra = self.peek()
        if extra is not None:
            raise CalcError("Unexpected '{}'.".format(extra.text))
        return result

    def parse_expression(self) -> Value:
        left = self.parse_term()

        while True:
            token = self.peek()
            if token is None or token.kind != "OP" or token.text not in "+-":
                return left

            operator = self.consume().text
            left = operate(left, operator, self.parse_term())

    def parse_term(self) -> Value:
        left = self.parse_unary()

        while True:
            token = self.peek()
            if token is None or token.kind != "OP" or token.text not in "*/×÷":
                return left

            operator = self.consume().text
            left = operate(left, operator, self.parse_unary())

    def parse_unary(self) -> Value:
        token = self.peek()
        if token is not None and token.kind == "OP" and token.text in "+-":
            operator = self.consume().text
            value = self.parse_unary()
            return negate(value) if operator == "-" else value
        return self.parse_primary()

    def parse_primary(self) -> Value:
        token = self.peek()
        if token is None:
            raise CalcError("The expression ends too early.")

        if token.kind == "LPAREN":
            self.consume()
            value = self.parse_expression()
            closing = self.peek()
            if closing is None or closing.kind != "RPAREN":
                raise CalcError("Missing ')'.")
            self.consume()
            return value

        token = self.consume()
        if token.kind == "NUMBER":
            return Number(float(token.text))
        if token.kind == "DURATION":
            return parse_duration(token.text)
        if token.kind == "TIME":
            return parse_clock(token.text)
        if token.kind == "DATE":
            return parse_date(token.text)

        raise CalcError("Unexpected '{}'.".format(token.text))


def parse_expression(source: str) -> Value:
    """Tokenize and parse one expression."""
    return Parser(tokenize(source)).parse()


def parse_duration(text: str) -> Span:
    """Parse a duration in O(k), where k is the number of parts."""
    matches = list(DURATION_RE.finditer(text.strip()))
    if not matches:
        raise CalcError("Use values such as 2h 30m, 3d or 1mo.")

    remainder = DURATION_RE.sub("", text).replace(",", "").strip()
    if remainder:
        raise CalcError("I do not understand '{}'.".format(remainder))

    values = {
        "years": 0.0, "months": 0.0, "weeks": 0.0,
        "days": 0.0, "hours": 0.0, "minutes": 0.0, "seconds": 0.0,
    }

    for match in matches:
        amount = float(match.group("number"))
        unit = UNIT_ALIASES[match.group("unit").lower()]
        values[unit] += amount

    return normalize_span(Span(**values))


def parse_clock(text: str) -> Clock:
    """Parse HH:MM[:SS] in O(1)."""
    match = TIME_RE.fullmatch(text.strip())
    if match is None:
        raise CalcError("Use a time such as 10:25 or 10:25:30.")

    minute = int(match.group("minute"))
    second = int(match.group("second") or 0)
    if minute > 59:
        raise CalcError("Minutes must be between 00 and 59.")
    if second > 59:
        raise CalcError("Seconds must be between 00 and 59.")

    hour = int(match.group("hour"))
    return Clock(hour * 3600 + minute * 60 + second)


def parse_date(text: str) -> Point:
    """Parse DD/MM/YYYY or DD-MM-YYYY with optional HH:MM[:SS]."""
    match = DATE_RE.fullmatch(text.strip())
    if match is None:
        raise CalcError("Use DD/MM/YYYY or DD-MM-YYYY.")

    year = int(match.group("year"))
    if year < 100:
        year += 2000 if year < 70 else 1900

    hour_text = match.group("hour")
    minute_text = match.group("minute")
    second_text = match.group("second")

    try:
        value = datetime(
            year,
            int(match.group("month")),
            int(match.group("day")),
            int(hour_text or 0),
            int(minute_text or 0),
            int(second_text or 0),
        )
    except ValueError:
        raise CalcError("That date or date/time does not exist.")

    return Point(value, hour_text is None)


def operate(left: Value, operator: str, right: Value) -> Value:
    """Apply one operation in O(1)."""
    if operator == "×":
        operator = "*"
    elif operator == "÷":
        operator = "/"

    if isinstance(left, Number) and isinstance(right, Number):
        if operator == "+": return Number(left.value + right.value)
        if operator == "-": return Number(left.value - right.value)
        if operator == "*": return Number(left.value * right.value)
        if operator == "/":
            if right.value == 0: raise CalcError("Cannot divide by zero.")
            return Number(left.value / right.value)

    if isinstance(left, Span) and isinstance(right, Span):
        if operator == "+": return add_span(left, right)
        if operator == "-": return subtract_span(left, right)
        raise CalcError("Durations support + and -. Use × or ÷ with a number to scale them.")

    if isinstance(left, Span) and isinstance(right, Number):
        if operator == "*": return scale_span(left, right.value)
        if operator == "/":
            if right.value == 0: raise CalcError("Cannot divide by zero.")
            return scale_span(left, 1.0 / right.value)
        raise CalcError("Use + or - with another duration.")

    if isinstance(left, Number) and isinstance(right, Span):
        if operator == "*": return scale_span(right, left.value)
        raise CalcError("A number can multiply a duration, but cannot divide by one.")

    if isinstance(left, Clock) and isinstance(right, Number):
        if operator == "*": return Clock(left.seconds * right.value)
        if operator == "/":
            if right.value == 0: raise CalcError("Cannot divide by zero.")
            return Clock(left.seconds / right.value)
        raise CalcError("Use × or ÷ when scaling a time.")

    if isinstance(left, Number) and isinstance(right, Clock):
        if operator == "*": return Clock(right.seconds * left.value)
        raise CalcError("A time can only be multiplied by a number.")

    if isinstance(left, Clock) and isinstance(right, Clock):
        if operator == "+": return Clock(left.seconds + right.seconds)
        if operator == "-": return Span(seconds=left.seconds - right.seconds)
        if operator == "/":
            if right.seconds == 0: raise CalcError("Cannot divide by zero.")
            return Number(left.seconds / right.seconds)
        raise CalcError("Two times cannot be multiplied.")

    if isinstance(left, Clock) and isinstance(right, Span):
        seconds = span_seconds(right)
        if operator == "+": return Clock(left.seconds + seconds)
        if operator == "-": return Clock(left.seconds - seconds)
        if operator == "/":
            if seconds == 0: raise CalcError("Cannot divide by zero.")
            return Number(left.seconds / seconds)

    if isinstance(left, Span) and isinstance(right, Clock):
        seconds = span_seconds(left)
        if operator == "+": return Clock(seconds + right.seconds)
        if operator == "-": return Span(seconds=seconds - right.seconds)
        if operator == "/":
            if right.seconds == 0: raise CalcError("Cannot divide by zero.")
            return Number(seconds / right.seconds)

    if isinstance(left, Point) and isinstance(right, Point):
        if operator == "-":
            return Span(seconds=(left.value - right.value).total_seconds())
        raise CalcError("Dates can only be subtracted from dates.")

    if isinstance(left, Point):
        if isinstance(right, Clock):
            right = Span(seconds=right.seconds)
        if isinstance(right, Span):
            if operator == "+":
                result = shift_datetime(left.value, right)
                has_time = (
                    not left.is_date
                    or abs(right.hours) > 1e-10
                    or abs(right.minutes) > 1e-10
                    or abs(right.seconds) > 1e-10
                )
                return Point(result, not has_time and left.is_date)
            if operator == "-":
                return operate(left, "+", negate(right))
        raise CalcError("A date supports + or - with a duration.")

    if isinstance(right, Point):
        if isinstance(left, (Span, Clock)) and operator == "+":
            return operate(right, "+", left)
        raise CalcError("Use + when combining a duration and a date.")

    raise CalcError(
        "I cannot use {} {} {}.".format(
            type(left).__name__, operator, type(right).__name__
        )
    )
