#!/usr/bin/env python3
"""Compatibility runner for deprecated nose on modern Python."""

import collections
import collections.abc
import sys

import nose


def main() -> int:
    # nose 1.3.7 still references collections.Callable, removed in modern Python.
    if not hasattr(collections, "Callable"):
        collections.Callable = collections.abc.Callable  # type: ignore[attr-defined]
    argv = ["nosetests", "-v", "tests"]
    return int(not nose.run(argv=argv))


if __name__ == "__main__":
    sys.exit(main())
