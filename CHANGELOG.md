# Changelog

## 0.2.0

- **Fixed:** importing `tsg` started the game. It now only starts from the `tsg` command.
- **Fixed:** a crash when finishing a round instantly, and silent `except:` clauses that hid errors.
- **Fixed:** accuracy ignored extra characters and the result line overlapped the Reset button.
- Typing now starts the clock without having to click the box first. Added Tab (new sentence) and Esc (quit).
- The long line you type scrolls inside its box instead of overflowing.
- `tsg --sentences FILE` to play with your own sentences, `--version`, `--help`.
- 30 sentences instead of 6.
- Game logic moved to `tsg.core` and covered by tests; the window is tested headless.
- Moved from Poetry to uv and hatchling. Python 3.10 to 3.13.
- Documentation, screenshots and CI.

## 0.1.1

Initial release.
