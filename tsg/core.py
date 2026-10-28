"""Game logic with no pygame in it, so it can be tested without a display."""

from __future__ import annotations

import json
import random
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .assets import assets


def accuracy(target: str, typed: str) -> float:
    """Percentage of characters typed correctly, 0 to 100.

    Compared by position. Extra characters beyond the target count against you.
    """
    longest = max(len(target), len(typed))
    if longest == 0:
        return 0.0
    correct = sum(1 for wanted, got in zip(target, typed, strict=False) if wanted == got)
    return correct / longest * 100


def wpm(typed: str, seconds: float) -> float:
    """Gross words per minute. A word is five characters, mistakes included."""
    if seconds <= 0:
        return 0.0
    return len(typed) / 5 / (seconds / 60)


def load_sentences(path: str | Path | None = None) -> list[str]:
    """Sentences to type. Defaults to the bundled ones.

    A custom file is either a `.json` list of strings, or plain text with one sentence per line.
    """
    file = Path(path) if path else Path(assets["sentences"])
    text = file.read_text(encoding="utf-8")
    if file.suffix.lower() == ".json":
        data = json.loads(text)
        if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
            raise ValueError(f"{file}: expected a JSON list of strings")
        sentences = data
    else:
        sentences = text.splitlines()
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    if not sentences:
        raise ValueError(f"{file}: no sentences found")
    return sentences


def pick_sentence(sentences: Sequence[str], rng: random.Random | None = None) -> str:
    return (rng or random).choice(sentences)


@dataclass(frozen=True)
class Result:
    seconds: float
    accuracy: float
    wpm: float

    def __str__(self) -> str:
        seconds, percent, speed = round(self.seconds), round(self.accuracy), round(self.wpm)
        return f"Time: {seconds} seconds - Accuracy: {percent}% - WPM: {speed}"


class Session:
    """One attempt at typing one sentence. Times are passed in, so tests do not need a clock."""

    def __init__(self, target: str) -> None:
        self.target = target
        self.typed = ""
        self.started_at: float | None = None
        self.result: Result | None = None

    @property
    def active(self) -> bool:
        return self.started_at is not None and self.result is None

    @property
    def finished(self) -> bool:
        return self.result is not None

    def start(self, now: float) -> None:
        """Start the clock. Starting again before finishing restarts the attempt."""
        if self.finished:
            return
        self.started_at = now
        self.typed = ""

    def type(self, text: str) -> None:
        if self.active:
            self.typed += text

    def backspace(self) -> None:
        if self.active:
            self.typed = self.typed[:-1]

    def finish(self, now: float) -> Result | None:
        """Stop the clock and score the attempt. Returns None if it never started."""
        if self.finished:
            return self.result
        if self.started_at is None:
            return None
        seconds = max(now - self.started_at, 0.001)
        self.result = Result(
            seconds=seconds,
            accuracy=accuracy(self.target, self.typed),
            wpm=wpm(self.typed, seconds),
        )
        return self.result
