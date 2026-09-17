"""Linear-time lexer for time/date arithmetic expressions."""

import re
from dataclasses import dataclass
from typing import List

from values import CalcError

DATE_RE = re.compile(
    r"""
    (?P<day>\d{1,2})
    (?P<sep>[/-])
    (?P<month>\d{1,2})
    (?P=sep)
    (?P<year>\d{2,4})
    (?:
        \s+
        (?P<hour>\d{1,2})
        :
        (?P<minute>\d{2})
        (?: : (?P<second>\d{2}) )?
    )?
    """,
    re.VERBOSE,
)

TIME_RE = re.compile(
    r"(?P<hour>\d+):(?P<minute>\d{2})(?::(?P<second>\d{2}))?"
)

NUMBER_RE = re.compile(r"(?:\d+(?:\.\d*)?|\.\d+)")

DURATION_RE = re.compile(
    r"""
    (?P<number>(?:\d+(?:\.\d*)?|\.\d+))\s*
    (?P<unit>
        years?|yrs?|yr|y|
        months?|mons?|mon|mo|
        weeks?|wk|w|
        days?|d|
        hours?|hrs?|hr|h|
        minutes?|mins?|min|m|
        seconds?|secs?|sec|s
    )
    (?![A-Za-z])
    """,
    re.VERBOSE | re.IGNORECASE,
)


@dataclass
class Token:
    kind: str
    text: str


def tokenize(source: str) -> List[Token]:
    """Tokenize left-to-right in O(n).

    Dates are recognized before '-' becomes an arithmetic operator,
    so both 17-09-2026 and 17/09/2026 remain single tokens.
    """
    tokens = []
    i = 0
    n = len(source)

    while i < n:
        if source[i].isspace():
            i += 1
            continue

        if source[i] == '(':
            tokens.append(Token("LPAREN", "("))
            i += 1
            continue

        if source[i] == ')':
            tokens.append(Token("RPAREN", ")"))
            i += 1
            continue

        rest = source[i:]

        # Reject date-looking input with mixed separators, e.g.
        # 17-09/2026. Without this guard it could be interpreted
        # as ordinary arithmetic (17 - 9 / 2026).
        malformed_date = re.match(
            r"\d{1,2}([/-])\d{1,2}([/-])\d{2,4}(?!\d)",
            rest,
        )
        if malformed_date is not None and malformed_date.group(1) != malformed_date.group(2):
            raise CalcError("Use the same separator in a date: DD/MM/YYYY or DD-MM-YYYY.")

        match = DATE_RE.match(rest)
        if match is not None:
            text = match.group(0)
            tokens.append(Token("DATE", text))
            i += len(text)
            continue

        match = TIME_RE.match(rest)
        if match is not None:
            text = match.group(0)
            tokens.append(Token("TIME", text))
            i += len(text)
            continue

        match = DURATION_RE.match(rest)
        if match is not None:
            text = match.group(0)
            tokens.append(Token("DURATION", text))
            i += len(text)
            continue

        match = NUMBER_RE.match(rest)
        if match is not None:
            text = match.group(0)
            tokens.append(Token("NUMBER", text))
            i += len(text)
            continue

        if source[i] in "+-*/×÷":
            tokens.append(Token("OP", source[i]))
            i += 1
            continue

        raise CalcError("I do not recognize '{}'.".format(rest))

    # Merge adjacent duration pieces: 2h 30m 15s -> one token.
    merged = []
    i = 0

    while i < len(tokens):
        token = tokens[i]
        if token.kind != "DURATION":
            merged.append(token)
            i += 1
            continue

        parts = [token.text]
        i += 1
        while i < len(tokens) and tokens[i].kind == "DURATION":
            parts.append(tokens[i].text)
            i += 1

        merged.append(Token("DURATION", " ".join(parts)))

    return merged
