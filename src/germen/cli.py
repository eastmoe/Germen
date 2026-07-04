"""Command-line dispatcher for Germen."""

from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="germen",
        description="Germen command launcher. Run without a subcommand to start the CLI workflow.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("cli", "ui", "gui", "web"),
        help="Subcommand: cli, ui, or web. Omit to run cli.",
    )
    parser.add_argument(
        "--admin",
        action="store_true",
        help="Request administrator privileges before launching Germen on Windows.",
    )
    return parser


def split_admin_flag(args: list[str]) -> tuple[bool, list[str]]:
    return "--admin" in args, [arg for arg in args if arg != "--admin"]


def is_help_request(args: list[str]) -> bool:
    return any(arg in ("-h", "--help") for arg in args)


def is_running_as_admin() -> bool:
    if os.name != "nt":
        return os.geteuid() == 0 if hasattr(os, "geteuid") else False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def relaunch_as_admin(args: list[str]) -> None:
    if os.name != "nt":
        raise RuntimeError("--admin 目前只支持 Windows UAC 提权。")

    argv0 = Path(sys.argv[0])
    if argv0.suffix.lower() == ".exe" and argv0.stem.lower() == "germen":
        executable = str(argv0)
        parameters = subprocess.list2cmdline(args)
    else:
        executable = sys.executable
        parameters = subprocess.list2cmdline(["-m", "germen.cli", *args])

    result = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        executable,
        parameters,
        os.getcwd(),
        1,
    )
    if result <= 32:
        raise RuntimeError(f"管理员权限启动失败，ShellExecuteW 返回: {result}")


def main(argv: Sequence[str] | None = None) -> None:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    admin_requested, args = split_admin_flag(raw_args)
    if args and args[0] in ("-h", "--help"):
        build_parser().print_help()
        return

    if admin_requested and not is_help_request(args) and not is_running_as_admin():
        relaunch_as_admin(args)
        return

    command = args[0] if args and not args[0].startswith("-") else None

    if command in ("web",):
        from .web.main import main as web_main

        web_main(args[1:], prog="germen web")
        return

    if command in ("ui", "gui"):
        if len(args) > 1:
            build_parser().error("ui 不接受额外参数。")
        from .gui import main as gui_main

        gui_main()
        return

    if command in (None, "cli"):
        if command == "cli":
            args = args[1:]
        if args:
            build_parser().error(f"未知参数: {' '.join(args)}")
        from .main_program import main as cli_main

        cli_main()
        return

    build_parser().error(f"未知命令: {command}")


if __name__ == "__main__":
    main()
