"""Small regression suite for the calculator engine."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from calculator import evaluate
from values import CalcError

CASES = {
    "10:25 + 1:20": "11:45:00",
    "1:30 / 5": "00:18:00",
    "10:25 - 1:20": "9 hours 5 minutes",
    "2h 30m + 45m": "3 hours 15 minutes",
    "90m / 3": "30 minutes",
    "17/09/2026 + 10d": "27/09/2026",
    "17-09-2026 + 2w": "01/10/2026",
    "17/09/2026 14:30 + 2h": "17/09/2026 16:30:00",
    "28/02/2026 - 17/02/2026": "11 days",
    "31/01/2026 + 1mo": "28/02/2026",
    "12 + 8 * 3": "36",
    "(12 + 8) * 3": "60",
    "-5 + 8": "3",
    "2h * 3": "6 hours",
    "1d - 2h": "22 hours",
    "1w + 1d": "8 days",
    "10:00 + 90m": "11:30:00",
    "10:00 - 90m": "08:30:00",
    "(1h 30m + 30m) / 2": "1 hour",
}


def run():
    for expression, expected in CASES.items():
        result, _, _ = evaluate(expression)
        assert result == expected, "{} -> {!r}, expected {!r}".format(
            expression, result, expected
        )

    for expression in (
        "1:30 / 0",
        "8 / 0",
        "1h / 0",
        "31/02/2026",
        "17-09/2026",
        "10:70",
        "10:25:70",
        "17/09/2026 * 2",
    ):
        try:
            evaluate(expression)
        except CalcError:
            pass
        else:
            raise AssertionError(
                "Invalid expression accepted: {}".format(expression)
            )

    print("All calculator tests passed.")


if __name__ == "__main__":
    run()
