"""tsg, a typing speed game."""

__version__ = "0.2.0"


def main() -> int:
    """Entry point of the `tsg` command."""
    from .cli import main as cli_main

    return cli_main()
