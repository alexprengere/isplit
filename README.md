<p align="center">
  <img src="https://raw.githubusercontent.com/alexprengere/isplit/main/docs/logo.svg" alt="isplit logo" width="520">
</p>

<p align="center">
  <strong>Lazy, typed string splitting helpers for Python, backed by Rust.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/isplit-rs/"><img src="https://img.shields.io/pypi/v/isplit-rs.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/isplit-rs/"><img src="https://img.shields.io/pypi/pyversions/isplit-rs.svg" alt="Python versions"></a>
  <a href="https://github.com/alexprengere/isplit/actions/workflows/python-package.yml"><img src="https://github.com/alexprengere/isplit/actions/workflows/python-package.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/alexprengere/isplit/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License"></a>
</p>

`isplit` scans a string once and yields pieces as soon as separators are found.
It is useful for tokenizer-style code where callers want to consume tokens
lazily instead of allocating the whole split result up front.

The iterator implementation is backed by a small PyO3 Rust extension when
available, with the original pure-Python implementation kept as a fallback.

## Installation

```shell
python -m pip install isplit-rs
```

The PyPI distribution is named `isplit-rs`, while the Python package is imported
as `isplit`.

## Quick start

```python
from isplit import irsplit, isplit

list(isplit("A+B+C+D", "+"))
# ["A", "B", "C", "D"]

list(isplit("AAA,,BBB", ",,"))
# ["AAA", "BBB"]

list(irsplit("A+B+C+D", "+"))
# ["D", "C", "B", "A"]
```

Or consume pieces lazily:

```python
from isplit import isplit

for token in isplit("AAA,BBB,CCC", ","):
    print(token)
```

## Why `isplit`?

| Feature | What it gives you |
| --- | --- |
| Lazy iteration | Consume split pieces one at a time |
| Forward and reverse splits | Use `isplit` or `irsplit` depending on scan direction |
| Rust acceleration | Use the PyO3 extension when available |
| Pure-Python fallback | Keep imports working even without the extension |
| Typed package | Ship a `py.typed` marker for type checkers |

## API

```python
isplit(text: str, sep: str) -> Iterator[str]
irsplit(text: str, sep: str) -> Iterator[str]
```

- `isplit(text, sep)` yields pieces from left to right.
- `irsplit(text, sep)` yields pieces from right to left.

Both functions follow `str.split` semantics for non-empty separators and raise
`ValueError` when `sep` is empty.
