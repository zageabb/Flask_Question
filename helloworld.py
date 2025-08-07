#!/usr/bin/env python3
"""Simple script to greet the world or a specified name."""

from __future__ import annotations

import argparse


def greet(name: str = "world") -> str:
    """Return a greeting message for the provided name."""
    return f"Hello, {name}!"


def main() -> None:
    """Parse command line arguments and print a greeting."""
    parser = argparse.ArgumentParser(description="Print a friendly greeting.")
    parser.add_argument(
        "--name",
        "-n",
        default="world",
        help="Name of the person to greet (default: world)",
    )
    args = parser.parse_args()
    print(greet(args.name))


if __name__ == "__main__":
    main()

