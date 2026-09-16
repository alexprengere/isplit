<p align="center">
  <img src="https://raw.githubusercontent.com/alexprengere/isplit/main/docs/logo.svg" alt="isplit logo" width="520">
</p>

<p align="center">
  <strong>Lazy string splitting for Python, backed by Rust.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/isplit-rs/"><img src="https://img.shields.io/pypi/v/isplit-rs.svg" alt="PyPI"></a>
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
pip install isplit-rs
```

> The PyPI distribution is named `isplit-rs`, while the Python package is imported as `isplit`.

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
    break
```

## Why `isplit`?

| Feature | What it gives you |
| --- | --- |
| Lazy iteration | Consume split pieces one at a time |
| Forward and reverse splits | Use `isplit` or `irsplit` depending on scan direction |
| Rust acceleration | Use the PyO3 extension when available |
| Pure-Python fallback | Keep imports working even without the extension |

## Performance

`isplit` is designed for lazy, partial consumption. When you need every piece
as a list, CPython's built-in `str.split` is usually the best choice. When you
only need the first few pieces from a larger string, `isplit` can stop before
splitting the rest of the input.

One local CPython 3.12 / macOS arm64 run, extracting only the first field with
the first separator at index 8:

| Input size | `split(",")[0]` | `split(",", 1)[0]` | `partition(",")[0]` | `next(isplit(...))` |
| ---: | ---: | ---: | ---: | ---: |
| ~1 MB | 1774.0 us | 14.6 us | 16.2 us | 0.3 us |
| ~100 KB | 140.7 us | 1.9 us | 2.0 us | 0.3 us |
| ~10 KB | 13.4 us | 0.8 us | 0.6 us | 0.3 us |
| ~1 KB | 1.8 us | 0.4 us | 0.3 us | 0.3 us |

<p align="center">
  <img src="https://raw.githubusercontent.com/alexprengere/isplit/main/docs/performance.svg" alt="Performance chart comparing partial str.split and isplit" width="760">
</p>

In other words, `isplit` helps most when it avoids unnecessary work. For small
strings, the difference is tiny; for larger strings, avoiding a full split can
matter.

Run the benchmark locally:

```shell
uv run python scripts/benchmark_split.py
```

## API

```python
isplit(text: str, sep: str) -> Iterator[str]
irsplit(text: str, sep: str) -> Iterator[str]
```

- `isplit(text, sep)` yields pieces from left to right.
- `irsplit(text, sep)` yields pieces from right to left.

Both functions follow `str.split` semantics for non-empty separators and raise
`ValueError` when `sep` is empty.

## Verify Rust acceleration

Installed wheels include the native Rust extension. To check that your
environment is using it:

```shell
python - <<'PY'
import isplit._rust as rust

print(rust.__file__)
print(list(rust.isplit("A+B+C", "+")))
PY
```

The printed path should point to a compiled extension such as
`isplit/_rust.abi3.so` on Linux/macOS or `isplit/_rust.pyd` on Windows.
