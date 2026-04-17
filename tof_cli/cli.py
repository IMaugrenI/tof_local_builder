from __future__ import annotations

import argparse

from tof_cli.commands import check, doctor, down, setup, status, ui, up


COMMAND_MODULES = [setup, up, check, down, status, doctor, ui]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python run.py",
        description="Cross-platform runtime CLI for tof_local_builder.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for module in COMMAND_MODULES:
        module.register(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 2
    return int(handler(args) or 0)
