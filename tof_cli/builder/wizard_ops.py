from __future__ import annotations

import sys

from tof_cli.core.env_ops import SCRIPTS_DIR

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import wizard as builder_wizard  # type: ignore


def ensure_wizard(force: bool = False) -> int:
    return int(builder_wizard.ensure_wizard(force=force))
