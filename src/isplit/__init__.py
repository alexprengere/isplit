"""Iterative string splitting helpers."""

from collections.abc import Iterator
from importlib.util import find_spec

__all__ = ["irsplit", "isplit"]

if find_spec(f"{__name__}._rust") is None:
    _rust = None
else:
    from . import _rust  # ty: ignore[unresolved-import]


def isplit(s: str, sep: str) -> Iterator[str]:
    """Lazy version of ``s.split(sep)``.

    >>> list(isplit("", ","))
    ['']
    >>> list(isplit("AAA", ","))
    ['AAA']
    >>> list(isplit("AAA,", ","))
    ['AAA', '']
    >>> list(isplit("AAA,BBB", ","))
    ['AAA', 'BBB']
    >>> list(isplit("AAA,,BBB", ",,"))
    ['AAA', 'BBB']
    """
    if _rust is not None:
        yield from _rust.isplit(s, sep)
        return

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


def irsplit(s: str, sep: str) -> Iterator[str]:
    """Lazy version of ``s.rsplit(sep)``.

    >>> list(irsplit("", ","))
    ['']
    >>> list(irsplit("AAA", ","))
    ['AAA']
    >>> list(irsplit("AAA,", ","))
    ['', 'AAA']
    >>> list(irsplit("AAA,BBB", ","))
    ['BBB', 'AAA']
    >>> list(irsplit("AAA,,BBB", ",,"))
    ['BBB', 'AAA']
    """
    if _rust is not None:
        yield from _rust.irsplit(s, sep)
        return

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
