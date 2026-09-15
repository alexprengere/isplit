from __future__ import annotations

import argparse
import gc
import platform
import statistics
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import isplit as isplit_pkg

try:
    import isplit._rust as rust
except ImportError:
    rust = None


def time_case(fn: Callable[[], object], rounds: int) -> list[float]:
    timings = []
    for _ in range(rounds):
        gc.collect()
        gc.disable()
        start = time.perf_counter_ns()
        fn()
        elapsed = time.perf_counter_ns() - start
        gc.enable()
        timings.append(elapsed / 1_000)
    return timings


def print_results(
    title: str,
    results: dict[str, list[float]],
    baseline_name: str,
) -> None:
    baseline = statistics.median(results[baseline_name])

    print(title)
    print("-" * len(title))
    print(f"{'case':<28} {'median us':>10} {'min us':>10} {'vs baseline':>12}")
    for name, values in results.items():
        median = statistics.median(values)
        best = min(values)
        print(f"{name:<28} {median:10.4f} {best:10.4f} {median / baseline:12.3f}x")
    print()


def parse_size(size: str) -> int:
    normalized = size.strip().lower()
    multipliers = {
        "b": 1,
        "k": 1_000,
        "kb": 1_000,
        "ko": 1_000,
        "m": 1_000_000,
        "mb": 1_000_000,
        "mo": 1_000_000,
    }
    for suffix, multiplier in sorted(
        multipliers.items(), key=lambda item: -len(item[0])
    ):
        if normalized.endswith(suffix):
            return int(normalized[: -len(suffix)]) * multiplier
    return int(normalized)


def make_text(target_size: int, token: str, sep: str) -> str:
    field_size = len(token) + len(sep)
    fields = max(1, (target_size + len(sep)) // field_size)
    return sep.join([token] * fields)


def python_isplit(s: str, sep: str):
    yield from isplit_pkg._py_isplit(s, sep)


def python_irsplit(s: str, sep: str):
    yield from isplit_pkg._py_irsplit(s, sep)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark stdlib splitting against isplit implementations.",
    )
    parser.add_argument("--fields", type=int, default=200_000)
    parser.add_argument(
        "--partial-sizes",
        default="1MB,100KB,10KB,1KB,100B",
        help="Comma-separated target sizes for the first-field benchmark.",
    )
    parser.add_argument("--token", default="abcdefgh")
    parser.add_argument("--sep", default=",")
    parser.add_argument("--rounds", type=int, default=10)
    args = parser.parse_args()

    text = args.sep.join([args.token] * args.fields)
    partial_sizes = [parse_size(size) for size in args.partial_sizes.split(",")]

    print(f"Python: {platform.python_version()} ({platform.python_implementation()})")
    print(f"Platform: {platform.platform()}")
    print(f"isplit: {isplit_pkg.__file__}")
    if rust is None:
        print("Rust extension: unavailable")
    else:
        print(f"Rust extension: {rust.__file__}")
    print()

    full_cases: dict[str, Callable[[], object]] = {
        "stdlib str.split": lambda: text.split(args.sep),
        "public isplit": lambda: list(isplit_pkg.isplit(text, args.sep)),
        "python fallback": lambda: list(python_isplit(text, args.sep)),
    }
    if rust is not None:
        full_cases["rust isplit"] = lambda: list(rust.isplit(text, args.sep))

    expected_full = text.split(args.sep)
    for name, fn in full_cases.items():
        assert fn() == expected_full, name

    print(
        f"Full split input: {len(text):,} chars, {args.fields:,} fields, "
        f"separator={args.sep!r}",
    )
    full_results = {name: time_case(fn, args.rounds) for name, fn in full_cases.items()}
    print_results("Full split, materialized list", full_results, "stdlib str.split")

    stream_cases: dict[str, Callable[[], object]] = {
        "stdlib split + consume": lambda: sum(map(len, text.split(args.sep))),
        "public isplit consume": lambda: sum(
            map(len, isplit_pkg.isplit(text, args.sep))
        ),
        "python fallback consume": lambda: sum(map(len, python_isplit(text, args.sep))),
    }
    if rust is not None:
        stream_cases["rust isplit consume"] = lambda: sum(
            map(len, rust.isplit(text, args.sep)),
        )

    expected_stream = len(args.token) * args.fields
    for name, fn in stream_cases.items():
        assert fn() == expected_stream, name

    stream_results = {
        name: time_case(fn, args.rounds) for name, fn in stream_cases.items()
    }
    print_results(
        "Full split, streaming consumption",
        stream_results,
        "stdlib split + consume",
    )

    for target_size in partial_sizes:
        partial_text = make_text(target_size, args.token, args.sep)
        partial_fields = partial_text.count(args.sep) + 1
        partial_cases: dict[str, Callable[[], object]] = {
            "str.split()[0]": lambda text=partial_text: text.split(args.sep)[0],
            "str.split(maxsplit=1)[0]": lambda text=partial_text: text.split(
                args.sep, 1
            )[0],
            "str.partition()[0]": lambda text=partial_text: text.partition(args.sep)[0],
            "public isplit first": lambda text=partial_text: next(
                isplit_pkg.isplit(text, args.sep)
            ),
            "python fallback first": lambda text=partial_text: next(
                python_isplit(text, args.sep)
            ),
        }
        if rust is not None:
            partial_cases["rust isplit first"] = lambda text=partial_text: next(
                rust.isplit(text, args.sep),
            )

        for name, fn in partial_cases.items():
            assert fn() == args.token, name

        print(
            f"Partial split input: {len(partial_text):,} chars, "
            f"{partial_fields:,} fields, first separator at index {len(args.token)}",
        )
        partial_results = {
            name: time_case(fn, args.rounds) for name, fn in partial_cases.items()
        }
        print_results("First field only", partial_results, "str.split(maxsplit=1)[0]")


if __name__ == "__main__":
    main()
