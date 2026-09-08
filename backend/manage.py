#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _reexec_with_venv_if_needed() -> None:
    """
    If the user runs `python manage.py ...` with system Python,
    restart using backend/venv so project dependencies are available.
    """
    backend_dir = Path(__file__).resolve().parent
    if os.name == "nt":
        venv_python = backend_dir / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = backend_dir / "venv" / "bin" / "python"

    if not venv_python.is_file():
        return

    current = Path(sys.executable).resolve()
    target = venv_python.resolve()
    if current == target:
        return

    os.execv(str(target), [str(target), *sys.argv])


def main() -> None:
    _reexec_with_venv_if_needed()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Activate backend/venv or install requirements:\n"
            "  .\\venv\\Scripts\\Activate.ps1\n"
            "  pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
