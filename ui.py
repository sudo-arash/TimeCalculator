"""Tkinter interface for the time/date calculator."""

import tkinter as tk
from collections import deque
from datetime import datetime

from calculator import evaluate
from values import CalcError

BG = "#0f1114"
SURFACE = "#171a1f"
SURFACE_2 = "#1d2127"
KEY = "#252a31"
KEY_HOVER = "#2d343c"
TEXT = "#f4f6f8"
MUTED = "#8d97a2"
BORDER = "#292f37"
ACCENT = "#eef1f4"
ACCENT_HOVER = "#ffffff"
ACCENT_TEXT = "#111316"


class CalculatorApp(tk.Tk):
    """A compact, keyboard-friendly calculator window."""

    def __init__(self):
        super().__init__()
        self.title("Time & Date Calculator")
        self.geometry("680x820")
        self.minsize(620, 740)
        self.configure(bg=BG)

        self.history = deque(maxlen=30)
        self.input_var = tk.StringVar()
        self.result_var = tk.StringVar(value="0")
        self.type_var = tk.StringVar(value="Ready")
        self.help_var = tk.StringVar(value="Try 10:25 + 1:20 or 1:30 / 5")
        self.clock_var = tk.StringVar()

        self.build()
        self.bind_keys()
        self.update_clock()
        self.after(100, self.focus_input)

    def build(self):
        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True, padx=28, pady=22)

        header = tk.Frame(root, bg=BG)
        header.pack(fill="x")

        tk.Label(
            header,
            text="Time & Date Calculator",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 20, "bold"),
        ).pack(side="left")

        tk.Label(
            header,
            textvariable=self.clock_var,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="right")

        card = tk.Frame(root, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(20, 14))

        tk.Label(
            card,
            text="CALCULATION",
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=20, pady=(16, 6))

        entry_wrap = tk.Frame(card, bg=SURFACE_2)
        entry_wrap.pack(fill="x", padx=18)

        self.entry = tk.Entry(
            entry_wrap,
            textvariable=self.input_var,
            bg=SURFACE_2,
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground=KEY,
            selectforeground=TEXT,
            relief="flat",
            bd=0,
            font=("Segoe UI", 20),
        )
        self.entry.pack(fill="x", padx=14, pady=12)

        tk.Label(
            card,
            textvariable=self.type_var,
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=20, pady=(12, 2))

        tk.Label(
            card,
            textvariable=self.result_var,
            bg=SURFACE,
            fg=TEXT,
            font=("Segoe UI", 29, "bold"),
            wraplength=590,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=20)

        tk.Label(
            card,
            textvariable=self.help_var,
            bg=SURFACE,
            fg=MUTED,
            font=("Segoe UI", 8),
            wraplength=590,
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(4, 16))

        self.section(root, "QUICK VALUES")
        quick = tk.Frame(root, bg=BG)
        quick.pack(fill="x", pady=(5, 12))

        for label, value in (
            ("1 min", "1m"), ("5 min", "5m"), ("30 min", "30m"),
            ("1 hour", "1h"), ("1 day", "1d"), ("1 week", "1w"),
            ("1 month", "1mo"), ("1 year", "1y"),
        ):
            tk.Button(
                quick,
                text=label,
                command=lambda v=value: self.insert(v),
                bg=SURFACE,
                fg=TEXT,
                activebackground=KEY_HOVER,
                activeforeground=TEXT,
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 8, "bold"),
                padx=7,
                pady=7,
            ).pack(side="left", padx=2)

        self.section(root, "EXAMPLES")
        examples = tk.Frame(root, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        examples.pack(fill="x", pady=(5, 12))

        grid = tk.Frame(examples, bg=SURFACE)
        grid.pack(fill="x", padx=12, pady=12)

        values = (
            "10:25 + 1:20", "1:30 / 5", "10:25 - 1:20",
            "2h 30m + 45m", "90m / 3", "17/09/2026 + 10d",
            "17-09-2026 + 2w", "17/09/2026 14:30 + 2h",
            "28/02/2026 - 17/02/2026", "31/01/2026 + 1mo",
            "(1h 30m + 30m) / 2", "12 + 8 * 3",
        )

        for i, expression in enumerate(values):
            tk.Button(
                grid,
                text=expression,
                command=lambda e=expression: self.example(e),
                bg=KEY,
                fg=TEXT,
                activebackground=KEY_HOVER,
                activeforeground=TEXT,
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 9),
                padx=8,
                pady=8,
            ).grid(row=i // 3, column=i % 3, padx=3, pady=3, sticky="ew")

        for column in range(3):
            grid.grid_columnconfigure(column, weight=1)

        self.section(root, "KEYPAD")
        keypad = tk.Frame(root, bg=BG)
        keypad.pack(fill="both", expand=True)

        layout = (
            ("7", "8", "9", "/"),
            ("4", "5", "6", "*"),
            ("1", "2", "3", "-"),
            ("0", ":", ".", "+"),
            ("(", ")", "⌫", "="),
        )

        for row in range(5):
            keypad.grid_rowconfigure(row, weight=1)
        for column in range(4):
            keypad.grid_columnconfigure(column, weight=1)

        for row, values in enumerate(layout):
            for column, text in enumerate(values):
                self.key(keypad, text, row, column)

        footer = tk.Frame(root, bg=BG)
        footer.pack(fill="x", pady=(9, 0))

        for label, command in (
            ("History", self.show_history),
            ("Copy result", self.copy_result),
        ):
            tk.Button(
                footer,
                text=label,
                command=command,
                bg=SURFACE,
                fg=TEXT,
                activebackground=KEY_HOVER,
                activeforeground=TEXT,
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 9, "bold"),
                padx=14,
                pady=8,
            ).pack(side="left", padx=(0, 6))

    def section(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")

    def key(self, parent, text, row, column):
        is_operator = text in {"+", "-", "*", "/"}
        is_result = text == "="

        bg = ACCENT if is_result else KEY_HOVER if is_operator else KEY
        fg = ACCENT_TEXT if is_result else TEXT
        hover = ACCENT_HOVER if is_result else KEY_HOVER

        tk.Button(
            parent,
            text=text,
            command=lambda t=text: self.press(t),
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=row, column=column, padx=3, pady=3, sticky="nsew")

    def press(self, text):
        if text == "=":
            self.calculate()
        elif text == "⌫":
            self.backspace()
        else:
            self.entry.insert(tk.END, text)
            self.focus_input()

    def insert(self, value):
        self.entry.insert(tk.END, value)
        self.focus_input()

    def example(self, expression):
        self.input_var.set(expression)
        self.calculate()

    def calculate(self):
        expression = self.input_var.get().strip()
        if not expression:
            return

        try:
            result, result_type, explanation = evaluate(expression)
        except CalcError as exc:
            self.type_var.set("Check the calculation")
            self.result_var.set("—")
            self.help_var.set(str(exc))
            self.focus_input()
            return

        self.type_var.set(result_type)
        self.result_var.set(result)
        self.help_var.set(explanation)
        self.history.appendleft((expression, result))
        self.focus_input()

    def backspace(self):
        value = self.input_var.get()
        if value:
            self.input_var.set(value[:-1])
        self.focus_input()

    def clear(self):
        self.input_var.set("")
        self.result_var.set("0")
        self.type_var.set("Ready")
        self.help_var.set("Try 10:25 + 1:20 or 1:30 / 5")
        self.focus_input()

    def copy_result(self):
        result = self.result_var.get()
        if result in {"", "—"}:
            return
        self.clipboard_clear()
        self.clipboard_append(result)
        self.update()
        self.help_var.set("Result copied to clipboard.")

    def show_history(self):
        if not self.history:
            self.help_var.set("No calculations yet.")
            return

        window = tk.Toplevel(self)
        window.title("History")
        window.geometry("420x520")
        window.configure(bg=BG)
        window.resizable(False, False)

        tk.Label(
            window,
            text="History",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", padx=20, pady=(20, 3))

        body = tk.Frame(window, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=10)

        for expression, result in self.history:
            tk.Button(
                body,
                text="{}\n= {}".format(expression, result),
                command=lambda e=expression: self.restore(e, window),
                bg=SURFACE,
                fg=TEXT,
                activebackground=KEY_HOVER,
                activeforeground=TEXT,
                relief="flat",
                bd=0,
                cursor="hand2",
                justify="right",
                anchor="e",
                font=("Segoe UI", 9),
                padx=12,
                pady=9,
            ).pack(fill="x", pady=3)

        tk.Button(
            window,
            text="Clear history",
            command=lambda: self.clear_history(window),
            bg=SURFACE_2,
            fg=MUTED,
            activebackground=KEY_HOVER,
            activeforeground=TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            pady=9,
        ).pack(fill="x", padx=14, pady=14)

    def restore(self, expression, window):
        self.input_var.set(expression)
        window.destroy()
        self.calculate()

    def clear_history(self, window):
        self.history.clear()
        window.destroy()
        self.help_var.set("History cleared.")

    def bind_keys(self):
        self.entry.bind("<Return>", lambda _event: self.calculate())
        self.entry.bind("<Escape>", lambda _event: self.clear())
        self.entry.bind("<Control-l>", lambda _event: self.clear())

    def focus_input(self):
        self.entry.focus_set()
        self.entry.icursor(tk.END)

    def update_clock(self):
        self.clock_var.set(datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)
