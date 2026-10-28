import json

import pytest

from tsg.core import Result, Session, accuracy, load_sentences, pick_sentence, wpm


def test_perfect_accuracy():
    assert accuracy("hello world", "hello world") == 100


def test_accuracy_counts_wrong_characters():
    assert accuracy("abcd", "abxd") == 75


def test_missing_characters_count_against_you():
    assert accuracy("abcd", "ab") == 50


def test_extra_characters_count_against_you():
    assert accuracy("ab", "abcd") == 50


def test_accuracy_of_nothing_is_zero():
    assert accuracy("", "") == 0
    assert accuracy("abc", "") == 0


def test_wpm_uses_five_characters_per_word():
    # 50 characters in one minute is 10 words per minute
    assert wpm("x" * 50, 60) == 10
    assert wpm("x" * 50, 30) == 20


def test_wpm_with_no_time_is_zero_not_a_crash():
    assert wpm("hello", 0) == 0
    assert wpm("hello", -1) == 0


def test_result_is_readable():
    assert str(Result(seconds=12.4, accuracy=96.6, wpm=48.2)) == "Time: 12 seconds - Accuracy: 97% - WPM: 48"


def test_session_scores_an_attempt():
    session = Session("abcde")
    session.start(now=100)
    session.type("abcde")
    result = session.finish(now=106)
    assert result == Result(seconds=6, accuracy=100, wpm=10)
    assert session.finished and not session.active


def test_session_ignores_typing_before_it_starts():
    session = Session("abc")
    session.type("abc")
    assert session.typed == ""
    assert session.finish(now=5) is None


def test_session_backspace():
    session = Session("abc")
    session.start(0)
    session.type("abx")
    session.backspace()
    session.type("c")
    assert session.typed == "abc"


def test_session_ignores_input_after_finishing():
    session = Session("abc")
    session.start(0)
    session.type("abc")
    first = session.finish(10)
    session.type("zzz")
    session.start(50)
    assert session.typed == "abc"
    assert session.finish(99) is first


def test_instant_finish_does_not_divide_by_zero():
    session = Session("abc")
    session.start(10)
    session.type("abc")
    result = session.finish(10)
    assert result is not None and result.seconds > 0


def test_starting_again_restarts_the_attempt():
    session = Session("abc")
    session.start(0)
    session.type("ab")
    session.start(5)
    assert session.typed == ""


def test_bundled_sentences_load():
    sentences = load_sentences()
    assert len(sentences) >= 20
    assert len(set(sentences)) == len(sentences)


def test_load_sentences_from_json(tmp_path):
    file = tmp_path / "mine.json"
    file.write_text(json.dumps(["one", " two ", ""]))
    assert load_sentences(file) == ["one", "two"]


def test_load_sentences_from_text(tmp_path):
    file = tmp_path / "mine.txt"
    file.write_text("first line\n\n  second line  \n")
    assert load_sentences(file) == ["first line", "second line"]


@pytest.mark.parametrize("content", ['{"a": 1}', "[1, 2]", "[]"])
def test_bad_json_sentences_are_rejected(tmp_path, content):
    file = tmp_path / "bad.json"
    file.write_text(content)
    with pytest.raises(ValueError):
        load_sentences(file)


def test_empty_text_file_is_rejected(tmp_path):
    file = tmp_path / "empty.txt"
    file.write_text("\n\n")
    with pytest.raises(ValueError):
        load_sentences(file)


def test_pick_sentence_picks_from_the_list():
    assert pick_sentence(["only"]) == "only"
