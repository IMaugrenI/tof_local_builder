from __future__ import annotations

import argparse

from tof_cli.ui.app import run_ui
from tof_cli.ui.launcher import ui_port
from tof_cli.core.env_ops import read_env


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("ui", help="start the local browser control UI")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="UI host address")
    parser.add_argument("--port", type=int, default=None, help="UI port (defaults to BUILDER_UI_PORT)")
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser automatically")
    parser.set_defaults(handler=handle)


def handle(args: argparse.Namespace) -> int:
    return run_ui(host=args.host, port=args.port if args.port is not None else ui_port(read_env()), open_browser=not args.no_browser)
