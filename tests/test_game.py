"""Run the real window with SDL's dummy drivers, so it works on CI without a display."""

import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # noqa: E402
import pytest  # noqa: E402

from tsg import __version__  # noqa: E402
from tsg.cli import main  # noqa: E402
from tsg.core import load_sentences  # noqa: E402
from tsg.game import INPUT_BOX, RESET_BOX, WIDTH, Game  # noqa: E402


@pytest.fixture
def game():
    game = Game(["hello world"])
    yield game
    pygame.quit()


def key(char):
    return pygame.event.Event(pygame.KEYDOWN, key=ord(char), unicode=char)


def special(code):
    return pygame.event.Event(pygame.KEYDOWN, key=code, unicode="")


def test_importing_the_package_does_not_open_a_window():
    import importlib

    import tsg

    importlib.reload(tsg)  # would hang or raise if main() ran on import
    assert tsg.__version__ == __version__


def test_bundled_sentences_fit_the_window():
    pygame.font.init()
    font = pygame.font.Font(None, 28)
    for sentence in load_sentences():
        assert font.size(sentence)[0] < WIDTH - 40, sentence


def test_typing_starts_the_round_and_enter_scores_it(game):
    for char in "hello world":
        game.handle(key(char))
    assert game.session.active
    game.handle(special(pygame.K_RETURN))
    assert game.session.finished
    assert game.session.result.accuracy == 100
    game.render()


def test_control_keys_are_not_typed(game):
    game.handle(key("h"))
    game.handle(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, unicode="\x1b"))
    assert game.session.typed == "h"


def test_enter_before_typing_does_nothing(game):
    game.handle(special(pygame.K_RETURN))
    assert not game.session.finished


def test_clicking_the_box_starts_the_clock(game):
    game.handle(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=INPUT_BOX.center, button=1))
    assert game.session.active


def test_reset_button_starts_a_new_round(game):
    game.handle(key("h"))
    game.handle(special(pygame.K_RETURN))
    old = game.session
    game.handle(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=RESET_BOX.center, button=1))
    assert game.session is not old and not game.session.finished


def test_tab_starts_a_new_round_and_escape_quits(game):
    game.running = True
    old = game.session
    game.handle(special(pygame.K_TAB))
    assert game.session is not old
    game.handle(special(pygame.K_ESCAPE))
    assert not game.running


def test_a_very_long_line_stays_inside_the_box(game):
    game.handle(key("h"))
    game.session.type("w" * 300)
    assert game.font(26).size(game.visible_typed_text())[0] <= INPUT_BOX.width - 20


def test_cli_reports_a_missing_sentences_file(tmp_path, capsys):
    assert main(["--sentences", str(tmp_path / "nope.txt")]) == 1
    assert "tsg:" in capsys.readouterr().err


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert __version__ in capsys.readouterr().out
