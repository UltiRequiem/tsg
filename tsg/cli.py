"""`tsg` command line."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from . import __version__
from .core import load_sentences


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tsg", description="A typing speed game.")
    parser.add_argument(
        "--sentences",
        metavar="FILE",
        help="your own sentences: a .json list of strings, or a text file with one sentence per line",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    try:
        sentences = load_sentences(args.sentences)
    except (OSError, ValueError) as error:
        print(f"tsg: {error}", file=sys.stderr)
        return 1

    # Imported here so --help and --version work without opening a window
    from .game import Game

    Game(sentences).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
