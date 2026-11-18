"""Command line interface for ``gitignore-gen``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from . import __version__
from .detector import detect, detected_names
from .templates import get_template, template_names
from .writer import HEADER, resolve_names, write_gitignore


def _build_parser() -> argparse.ArgumentParser:
    """Create the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="gitignore-gen",
        description=(
            "Generate and maintain .gitignore files from curated templates. "
            "Combine multiple stacks, de-duplicate rules, and keep custom lines."
        ),
        epilog=(
            "Examples:\n"
            "  gitignore-gen list\n"
            "  gitignore-gen show python\n"
            "  gitignore-gen detect .\n"
            "  gitignore-gen add python,node --output .gitignore\n"
            "  gitignore-gen init ."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="print the program version and exit",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    sub.add_parser("list", help="list available templates")

    show = sub.add_parser("show", help="print a single template")
    show.add_argument("name", help="template name, e.g. python")

    detect_cmd = sub.add_parser(
        "detect",
        help="scan a directory and suggest templates",
    )
    detect_cmd.add_argument(
        "path",
        nargs="?",
        default=".",
        help="directory to scan (default: current directory)",
    )

    add = sub.add_parser("add", help="merge templates into a .gitignore file")
    add.add_argument(
        "names",
        nargs="+",
        metavar="NAME[,NAME...]",
        help="one or more template names; comma-separated values accepted",
    )
    add.add_argument(
        "--output",
        "-o",
        default=".gitignore",
        help="output file (default: .gitignore)",
    )
    add.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would be added without writing the file",
    )

    init = sub.add_parser(
        "init",
        help="detect project types and write .gitignore automatically",
    )
    init.add_argument(
        "path",
        nargs="?",
        default=".",
        help="project directory (default: current directory)",
    )

    return parser


def _cmd_list() -> int:
    names = template_names()
    width = max(len(name) for name in names) + 2
    for name in names:
        template = get_template(name)
        print(f"{name:<{width}}{template.description}")
    print(f"\n{len(names)} templates available.")
    return 0


def _cmd_show(name: str) -> int:
    try:
        template = get_template(name)
    except KeyError:
        print(f"error: unknown template: {name!r}", file=sys.stderr)
        print("run 'gitignore-gen list' to see available templates", file=sys.stderr)
        return 2
    sys.stdout.write(template.render())
    return 0


def _cmd_detect(path: str) -> int:
    try:
        results = detect(path)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    target = Path(path)
    if not results:
        print(f"No known project markers found in {target}.")
        return 0

    print(f"Detected templates for {target}:")
    width = max(len(item.template) for item in results) + 2
    for item in results:
        print(f"  {item.template:<{width}}{item.reason}")

    names = ",".join(item.template for item in results)
    print()
    print("Suggested command:")
    print(f"  gitignore-gen add {names}")
    return 0


def _cmd_add(raw_names: Sequence[str], output: str, dry_run: bool) -> int:
    try:
        names = resolve_names(raw_names)
    except KeyError as exc:
        unknown = exc.args[0] if exc.args else ""
        print(f"error: unknown template: {unknown!r}", file=sys.stderr)
        print("run 'gitignore-gen list' to see available templates", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        result = write_gitignore(output, names, dry_run=dry_run)
    except (IsADirectoryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    verb = "Would add" if dry_run else "Added"
    print(f"{verb} {result.added} line(s) to {result.path}")
    if result.added == 0:
        print("Everything is already up to date.")
    elif dry_run:
        print("Dry run: no files were modified.")
    return 0


def _cmd_init(path: str) -> int:
    target = Path(path)
    try:
        results = detect(target)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not results:
        print(f"No known project markers found in {target}. Nothing written.")
        return 0

    names = [item.template for item in results]
    output = target / ".gitignore"
    try:
        result = write_gitignore(output, names)
    except (IsADirectoryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Detected: {', '.join(detected_names(target))}")
    print(f"Wrote {result.path} (+{result.added} line(s), {result.total} rule lines)")
    print(f"Header: {HEADER}")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Program entry point.

    Args:
        argv: Optional argument vector (excluding the program name). When
            ``None``, :data:`sys.argv` is used.

    Returns:
        Process exit code: ``0`` on success, ``2`` on usage or lookup errors.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        return _cmd_list()
    if args.command == "show":
        return _cmd_show(args.name)
    if args.command == "detect":
        return _cmd_detect(args.path)
    if args.command == "add":
        return _cmd_add(args.names, args.output, args.dry_run)
    if args.command == "init":
        return _cmd_init(args.path)

    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover - module entry guard
    sys.exit(main())
