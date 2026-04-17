from __future__ import annotations

import argparse

from tof_cli.ui.app import run_ui


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("ui", help="start the local browser control UI")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="UI host address")
    parser.add_argument("--port", type=int, default=8795, help="UI port")
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser automatically")
    parser.set_defaults(handler=handle)


def handle(args: argparse.Namespace) -> int:
    return run_ui(host=args.host, port=args.port, open_browser=not args.no_browser)
