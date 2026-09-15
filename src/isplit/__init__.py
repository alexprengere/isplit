"""Iterative string splitting helpers."""

from collections.abc import Callable, Iterator
from importlib.util import find_spec

__all__ = ["irsplit", "isplit"]


def _py_isplit(s: str, sep: str) -> Iterator[str]:
    """Lazy version of ``s.split(sep)``.

    >>> list(_py_isplit("", ","))
    ['']
    >>> list(_py_isplit("AAA", ","))
    ['AAA']
    >>> list(_py_isplit("AAA,", ","))
    ['AAA', '']
    >>> list(_py_isplit("AAA,BBB", ","))
    ['AAA', 'BBB']
    >>> list(_py_isplit("AAA,,BBB", ",,"))
    ['AAA', 'BBB']
    """
    seplen = len(sep)
    if seplen == 0:
        raise ValueError("empty separator")

    start = 0
    while True:
        index = s.find(sep, start)
        if index == -1:
            yield s[start:]
            return
        yield s[start:index]
        start = index + seplen


def _py_irsplit(s: str, sep: str) -> Iterator[str]:
    """Lazy version of ``s.rsplit(sep)``.

    >>> list(_py_irsplit("", ","))
    ['']
    >>> list(_py_irsplit("AAA", ","))
    ['AAA']
    >>> list(_py_irsplit("AAA,", ","))
    ['', 'AAA']
    >>> list(_py_irsplit("AAA,BBB", ","))
    ['BBB', 'AAA']
    >>> list(_py_irsplit("AAA,,BBB", ",,"))
    ['BBB', 'AAA']
    """
    seplen = len(sep)
    if seplen == 0:
        raise ValueError("empty separator")

    end = len(s)
    while True:
        index = s.rfind(sep, 0, end)
        if index == -1:
            yield s[:end]
            return
        yield s[index + seplen : end]
        end = index


if find_spec(f"{__name__}._rust") is None:
    isplit: Callable[[str, str], Iterator[str]] = _py_isplit
    irsplit: Callable[[str, str], Iterator[str]] = _py_irsplit
else:
    from . import _rust  # ty: ignore[unresolved-import]

    isplit: Callable[[str, str], Iterator[str]] = _rust.isplit
    irsplit: Callable[[str, str], Iterator[str]] = _rust.irsplit
