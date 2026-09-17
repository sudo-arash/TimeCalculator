# Time & Date Calculator

A lightweight desktop calculator built with **Python 3.8+** and **Tkinter** for arithmetic involving numbers, times, durations, and dates.

The goal is simple: enter an expression naturally and get the result without having to use a complicated date/time interface.

## Features

- Normal arithmetic

```text
12 + 8 * 3
(12 + 8) * 3
8 / 2
```

- Time arithmetic

```text
10:25 + 1:20
10:25 - 1:20
1:30 / 5
10:00 + 90m
```

- Duration arithmetic

```text
2h 30m + 45m
90m / 3
2h * 3
1w + 1d
```

- Date arithmetic

```text
17/09/2026 + 10d
17-09-2026 + 2w
31/01/2026 + 1mo
```

- Date and time arithmetic

```text
17/09/2026 14:30 + 2h
```

- Date subtraction

```text
28/02/2026 - 17/02/2026
```

- Parentheses and operator precedence

```text
(1h 30m + 30m) / 2
12 + 8 * 3
```

- Calendar-aware months and years
- Negative values
- Calculation history
- Copy result to clipboard
- Clickable keypad
- Quick duration shortcuts
- Clickable examples
- Keyboard input
- No third-party dependencies

## Examples

| Expression                | Result                |
| ------------------------- | --------------------- |
| `10:25 + 1:20`            | `11:45:00`            |
| `1:30 / 5`                | `00:18:00`            |
| `10:25 - 1:20`            | `09:05:00`            |
| `2h 30m + 45m`            | `03:15:00`            |
| `90m / 3`                 | `00:30:00`            |
| `17/09/2026 + 10d`        | `27/09/2026`          |
| `17-09-2026 + 2w`         | `01/10/2026`          |
| `17/09/2026 14:30 + 2h`   | `17/09/2026 16:30:00` |
| `28/02/2026 - 17/02/2026` | `11 days`             |
| `31/01/2026 + 1mo`        | `28/02/2026`          |
| `(1h 30m + 30m) / 2`      | `01:00:00`            |
| `12 + 8 * 3`              | `36`                  |

## Supported units

### Years

```text
y
yr
year
years
```

### Months

```text
mo
mon
month
months
```

### Weeks

```text
w
wk
week
weeks
```

### Days

```text
d
day
days
```

### Hours

```text
h
hr
hour
hours
```

### Minutes

```text
m
min
minute
minutes
```

### Seconds

```text
s
sec
second
seconds
```

`m` means **minutes** and `mo` means **months**.

## Dates

Both `/` and `-` are supported:

```text
17/09/2026
17-09-2026
```

Date-times are also supported:

```text
17/09/2026 14:30
17-09-2026 14:30:25
```

A date must use the same separator throughout.

Valid:

```text
17-09-2026
17/09/2026
```

Invalid:

```text
17-09/2026
```

## Times

Times use:

```text
HH:MM
HH:MM:SS
```

Examples:

```text
10:25
1:30
10:25:30
```

A time value is treated as an arithmetic quantity, so operations such as these are valid:

```text
10:25 + 1:20
10:25 - 1:20
1:30 / 5
2:00 * 3
```

For arithmetic, hours may exceed 23.

For example:

```text
23:30 + 2h
```

produces:

```text
1d 01:30:00
```

## Operators

The calculator supports:

```text
+
-
*
/
×
÷
```

Standard arithmetic precedence is used:

```text
12 + 8 * 3
```

is interpreted as:

```text
12 + (8 * 3)
```

Parentheses can be used when a different order is required:

```text
(12 + 8) * 3
```

## Architecture

The project is deliberately separated into small modules:

```text
TimeClock/
├── main.py
├── ui.py
├── calculator.py
├── expression_parser.py
├── lexer.py
├── values.py
├── formatter.py
├── README.md
└── tests/
    └── test_calculator.py
```

### `main.py`

The application entry point.

It only starts the Tkinter application:

```python
from ui import CalculatorApp

if __name__ == "__main__":
    CalculatorApp().mainloop()
```

### `ui.py`

Contains the Tkinter interface.

Responsibilities include:

- calculator layout
- keypad
- expression input
- examples
- quick values
- result display
- history
- clipboard
- keyboard shortcuts
- current clock display

The UI does not implement arithmetic itself.

### `calculator.py`

Provides the small public calculator API.

The UI can simply call:

```python
evaluate(expression)
```

and receive the formatted result.

### `expression_parser.py`

Contains the expression parser and arithmetic dispatch.

It uses a **recursive-descent parser** with the following structure:

```text
expression
    └── term
         └── unary
              └── primary
```

This provides normal arithmetic precedence and supports parentheses and unary operators.

### `lexer.py`

Converts the raw expression into tokens.

A particularly important rule is that dates are recognized **before** arithmetic operators.

For example:

```text
17-09-2026
```

must be recognized as one date token rather than:

```text
17 - 09 - 2026
```

This prevents date separators from being confused with subtraction.

### `values.py`

Contains the calculator's core data types:

```text
Number
Span
Clock
Point
```

It also contains:

- duration normalization
- duration arithmetic
- calendar-aware date shifting
- conversion between compatible value types
- numeric cleanup

The UI has no knowledge of these implementation details.

### `formatter.py`

Converts internal values into user-facing strings.

Examples:

```text
Duration -> 03:15:00
Date     -> 27/09/2026
Number   -> 36
```

## Complexity

The implementation is designed around linear parsing and constant-time arithmetic.

For an expression containing `n` input characters:

### Tokenization

```text
O(n)
```

The lexer scans the input from left to right.

### Parsing

```text
O(n)
```

Each token is consumed at most once by the parser.

### Arithmetic

```text
O(1)
```

Each arithmetic operation works on a fixed number of fields.

### Date shifting

```text
O(1)
```

Month and year calculations use direct calendar arithmetic rather than iterating through individual days.

### Formatting

```text
O(1)
```

There is a fixed number of units to format.

### Memory

Parsing requires:

```text
O(n)
```

memory for the token representation and parser state.

The history uses a bounded collection, so it does not grow indefinitely.

## Running the application

Python 3.8 or newer is required.

No external packages are necessary because the project uses Python's standard library and Tkinter.

Run:

```powershell
python main.py
```

## Running the tests

The project contains regression tests for the parser and arithmetic engine.

Run:

```powershell
python tests/test_calculator.py
```

The tests cover:

- time addition
- time subtraction
- time division
- duration arithmetic
- duration normalization
- date arithmetic
- dashed dates
- slash dates
- datetime arithmetic
- month arithmetic
- parenthesized expressions
- normal number arithmetic
- unary minus
- division-by-zero handling
- invalid date/time values

## Design principles

The project intentionally keeps the interface restrained.

The main interaction is:

```text
Type expression
      ↓
Press Enter
      ↓
See result
```

The keypad, examples, quick values, history, and keyboard shortcuts are secondary conveniences rather than competing with the main calculation.

The parser is also intentionally independent from Tkinter so that the calculation engine can be tested without launching the UI.

## Error handling

Invalid input should produce a readable calculator error instead of a Python traceback.

Examples:

```text
1:30 / 0
```

produces:

```text
Cannot divide by zero.
```

An invalid date such as:

```text
31/02/2026
```

produces a user-facing date error.

The original expression remains available so it can be corrected without retyping it.

## Why a custom parser?

Using Python's `eval()` would make the expression handling unnecessarily unsafe and difficult to extend.

Instead, the calculator uses:

```text
Input
  ↓
Lexer
  ↓
Tokens
  ↓
Recursive-descent parser
  ↓
Typed values
  ↓
Arithmetic
  ↓
Formatter
  ↓
Result
```

This makes date/time syntax and type-specific arithmetic explicit and predictable.

## Future improvements

Possible future additions include:

- locale-aware date input
- 12-hour AM/PM input
- Persian date support
- timezone calculations
- date difference modes
- a dedicated date picker
- more advanced calendar operations
- saved persistent history
- light theme
- configurable date/time formatting
- standalone packaging with PyInstaller

## License

This project is currently provided without a specified open-source license.
Add a license file before distributing it publicly.
