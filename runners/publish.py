#!/usr/bin/env python3
"""Publish worksheets to docs/ for GitHub Pages.

Scans worksheets/<child>/ for HTML files (regardless of how they were
created), copies them flat into docs/, copies any archive/ subfolder into
docs/archive/, and regenerates docs/index.html and docs/archive/index.html.

Usage:
    python runners/publish.py            # copy + regenerate index
    python runners/publish.py --push     # also git add/commit/push docs/

The AUTO_COMMIT=true environment variable is equivalent to --push.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slug_to_label(slug: str) -> str:
    """Turn '2026-03-17-guess-check-auditions' into 'Mar 17, 2026 — Guess Check Auditions'."""
    date_match = re.match(r"^(\d{4})[_-](\d{2})[_-](\d{2})[_-]?(.*)$", slug)
    if not date_match:
        return slug.replace("-", " ").replace("_", " ").title()

    year, month, day, rest = date_match.groups()
    try:
        from datetime import date
        d = date(int(year), int(month), int(day))
        date_label = d.strftime("%b %-d, %Y")
    except (ValueError, AttributeError):
        # strftime %-d is Linux/macOS only; fall back for Windows
        from datetime import date
        d = date(int(year), int(month), int(day))
        date_label = d.strftime("%b %#d, %Y") if sys.platform == "win32" else d.strftime("%b %-d, %Y")

    subject = rest.replace("-", " ").replace("_", " ").title() if rest else ""
    return f"{date_label} — {subject}" if subject else date_label


def regenerate_index(docs_files: list[Path], has_archive: bool = False) -> None:
    entries = sorted(docs_files, key=lambda p: p.name, reverse=True)
    items = "\n".join(
        f'    <li><a href="{p.name}">{slug_to_label(p.stem)}</a></li>'
        for p in entries
    )
    archive_footer = """
  <hr style="margin-top:2rem;border:none;border-top:1px solid #ddd;">
  <p style="font-size:.9rem;"><a href="archive/index.html">Older worksheets &rarr;</a></p>""" if has_archive else ""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Worksheets</title>
  <style>
    body {{ font-family: sans-serif; max-width: 600px; margin: 2rem auto; padding: 0 1rem; }}
    h1 {{ font-size: 1.4rem; margin-bottom: 1rem; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ margin: 0.5rem 0; }}
    a {{ color: #0066cc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>Worksheets</h1>
  <ul>
{items}
  </ul>{archive_footer}
</body>
</html>"""
    index_path = DOCS_DIR / "index.html"
    index_path.write_text(html, encoding="utf8")
    print(f"📄 Index written: {index_path.relative_to(ROOT).as_posix()}")


def regenerate_archive_index(archive_files: list[Path]) -> None:
    entries = sorted(archive_files, key=lambda p: p.name, reverse=True)
    items = "\n".join(
        f'    <li><a href="{p.name}">{slug_to_label(p.stem)}</a></li>'
        for p in entries
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Archived Worksheets</title>
  <style>
    body {{ font-family: sans-serif; max-width: 600px; margin: 2rem auto; padding: 0 1rem; }}
    h1 {{ font-size: 1.4rem; margin-bottom: 1rem; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ margin: 0.5rem 0; }}
    a {{ color: #0066cc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>Archived Worksheets</h1>
  <ul>
{items}
  </ul>
  <hr style="margin-top:2rem;border:none;border-top:1px solid #ddd;">
  <p style="font-size:.9rem;"><a href="../index.html">&larr; Back</a></p>
</body>
</html>"""
    archive_index = DOCS_DIR / "archive" / "index.html"
    archive_index.write_text(html, encoding="utf8")
    print(f"📄 Archive index written: {archive_index.relative_to(ROOT).as_posix()}")


def commit_and_push(root: Path) -> None:
    commands = [
        ["git", "-C", str(root), "add", "docs/"],
        ["git", "-C", str(root), "commit", "-m", "Publish worksheets to docs/"],
        ["git", "-C", str(root), "push"],
    ]
    try:
        for command in commands:
            subprocess.run(command, check=True, capture_output=True, text=True)
        print("🚀 Committed and pushed docs/")
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() or error.stdout.strip() or str(error)
        print(f"⚠️  Git operation failed: {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish worksheets to docs/ for GitHub Pages.")
    parser.add_argument(
        "--child", "-c",
        default=None,
        help="Child subdirectory name under worksheets/ (overrides DEFAULT_CHILD env var).",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        default=False,
        help="Git add/commit/push docs/ after publishing (also enabled by AUTO_COMMIT=true).",
    )
    parser.add_argument(
        "--preserve",
        action="store_true",
        default=False,
        help="Skip wiping docs/*.html before copying (keep files not present in source).",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()
    should_push = args.push or os.environ.get("AUTO_COMMIT") == "true"

    child = args.child or os.environ.get("DEFAULT_CHILD")
    if not child:
        print("❌ Child name required: pass --child <name> or set DEFAULT_CHILD env var.", file=sys.stderr)
        return 1

    source_dir = ROOT / "worksheets" / child

    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}", file=sys.stderr)
        return 1

    source_files = sorted(source_dir.glob("*.html"))
    if not source_files:
        print(f"⚠️  No HTML files found in {source_dir.relative_to(ROOT).as_posix()}/", file=sys.stderr)
        return 0

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    if not args.preserve:
        removed = 0
        for stale in DOCS_DIR.glob("*.html"):
            stale.unlink()
            removed += 1
        if (DOCS_DIR / "archive").exists():
            for stale in (DOCS_DIR / "archive").glob("*.html"):
                stale.unlink()
                removed += 1
        if removed:
            print(f"  🗑️  Removed {removed} stale file(s) from docs/")

    # Copy main worksheets
    copied = 0
    skipped = 0
    docs_files: list[Path] = []

    for src in source_files:
        dest = DOCS_DIR / src.name
        docs_files.append(dest)

        if args.preserve and dest.exists() and file_hash(src) == file_hash(dest):
            print(f"  ✓ Unchanged: {src.name}")
            skipped += 1
            continue

        dest.write_bytes(src.read_bytes())
        print(f"  📋 Copied:   {src.name}")
        copied += 1

    # Copy archive/ if present
    archive_source = source_dir / "archive"
    archive_docs_files: list[Path] = []
    has_archive = False

    if archive_source.exists():
        archive_files = sorted(archive_source.glob("*.html"))
        if archive_files:
            has_archive = True
            archive_dest_dir = DOCS_DIR / "archive"
            archive_dest_dir.mkdir(parents=True, exist_ok=True)
            print(f"  📦 Archive:")
            for src in archive_files:
                dest = archive_dest_dir / src.name
                archive_docs_files.append(dest)

                if args.preserve and dest.exists() and file_hash(src) == file_hash(dest):
                    print(f"    ✓ Unchanged: {src.name}")
                    continue

                dest.write_bytes(src.read_bytes())
                print(f"    📋 Copied:   {src.name}")

            regenerate_archive_index(archive_docs_files)

    regenerate_index(docs_files, has_archive=has_archive)
    skipped_note = f", {skipped} unchanged" if args.preserve else ""
    archive_note = f", {len(archive_docs_files)} archived" if has_archive else ""
    print(f"\n✅ Done — {copied} copied{skipped_note}{archive_note}, {len(docs_files)} total")

    if should_push:
        commit_and_push(ROOT)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
