import pytest

import isplit as isplit_module
from isplit import irsplit, isplit


@pytest.mark.parametrize(
    ("s", "sep", "expected"),
    [
        ("", ",", [""]),
        ("AAA", ",", ["AAA"]),
        ("AAA,", ",", ["AAA", ""]),
        ("AAA,BBB", ",", ["AAA", "BBB"]),
        ("AAA,,BBB", ",,", ["AAA", "BBB"]),
    ],
)
def test_isplit_matches_str_split(s: str, sep: str, expected: list[str]) -> None:
    assert list(isplit(s, sep)) == expected
    assert list(isplit(s, sep)) == s.split(sep)


@pytest.mark.parametrize(
    ("s", "sep", "expected"),
    [
        ("", ",", [""]),
        ("AAA", ",", ["AAA"]),
        ("AAA,", ",", ["", "AAA"]),
        ("AAA,BBB", ",", ["BBB", "AAA"]),
        ("AAA,,BBB", ",,", ["BBB", "AAA"]),
    ],
)
def test_irsplit_matches_reversed_str_rsplit(
    s: str,
    sep: str,
    expected: list[str],
) -> None:
    assert list(irsplit(s, sep)) == expected
    assert list(irsplit(s, sep)) == list(reversed(s.rsplit(sep)))


def test_isplit_is_its_own_iterator() -> None:
    iterator = isplit("AAA,BBB", ",")

    assert iter(iterator) is iterator
    assert next(iterator) == "AAA"
    assert next(iterator) == "BBB"

    with pytest.raises(StopIteration):
        next(iterator)


def test_irsplit_is_its_own_iterator() -> None:
    iterator = irsplit("AAA,BBB", ",")

    assert iter(iterator) is iterator
    assert next(iterator) == "BBB"
    assert next(iterator) == "AAA"

    with pytest.raises(StopIteration):
        next(iterator)


def test_unicode_input_and_separator() -> None:
    assert list(isplit("AéBéC", "é")) == ["A", "B", "C"]
    assert list(irsplit("AéBéC", "é")) == ["C", "B", "A"]


def test_empty_separator_is_invalid() -> None:
    with pytest.raises(ValueError, match="empty separator"):
        list(isplit("A+B", ""))
    with pytest.raises(ValueError, match="empty separator"):
        list(irsplit("A+B", ""))


def test_public_api_uses_rust_directly_when_available() -> None:
    rust = pytest.importorskip("isplit._rust")

    assert isplit_module.isplit is rust.isplit
    assert isplit_module.irsplit is rust.irsplit
