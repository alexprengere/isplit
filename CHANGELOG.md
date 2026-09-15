# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-09-15

- Optimized the Rust string iterators to avoid copying the full input string by
  using CPython Unicode C-API operations for find/substr work.
- Bound the public API directly to the Rust extension on CPython, while using
  the Python fallback on PyPy.
- README performance section with microsecond timings and a chart for partial
  first-field splitting across ~100 B, ~1 KB, ~10 KB, ~100 KB, and ~1 MB inputs.
- README guidance for verifying that the installed wheel is using the native
  Rust extension.

## [0.2.0] - 2026-09-15

- README guidance for verifying Rust acceleration.
- PyPI project links for the repository and changelog.

## [0.1.0] - 2026-09-15

Initial PyPI release.

- Lazy `isplit` and `irsplit` helpers for iterative string splitting.
- Rust-backed PyO3 extension with a pure-Python fallback.
- Typed package marker for type checkers.
- Binary wheel publishing for Linux, macOS, and Windows.
- MIT license metadata and project documentation.
