#!/usr/bin/env python3
"""Worksheet Accessibility App Builder CLI runner."""

from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from datetime import date
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent
DEBUG_RESPONSE_FILE = ROOT / "tmp" / "debug-response.txt"
PENDING_UPDATES_FILE = ROOT / "pending-updates.md"
UPDATE_BLOCK_RE = re.compile(
    r"<!--\s*COPILOT_UPDATE_SUGGESTED_START(?P<body>.*?)COPILOT_UPDATE_SUGGESTED_END\s*-->",
    flags=re.DOTALL,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build an accessible worksheet app from a worksheet PDF or image."
        )
    )
    parser.add_argument("--worksheet", "-w", required=True)
    parser.add_argument("--child", "-c", default=os.environ.get("DEFAULT_CHILD", "maya")
    )
    parser.add_argument("--date", "-d", dest="date_str", default=today_iso())
    parser.add_argument("--subject", "-s", default="worksheet")
    return parser.parse_args()


def read_file(rel_path: str) -> str:
    full_path = ROOT / rel_path
    if not full_path.exists():
        print(f"⚠️  Missing: {rel_path}", file=sys.stderr)
        return ""
    return full_path.read_text(encoding="utf8")


def assemble_system_prompt(child: str) -> str:
    return "\n\n".join(
        [
            read_file("SYSTEM_PROMPT.md"),
            "---",
            "## Framework: Design System\n\n" + read_file("framework/DESIGN_SYSTEM.md"),
            "## Framework: Interaction Patterns\n\n"
            + read_file("framework/INTERACTION_PATTERNS.md"),
            "## Framework: Build Constraints\n\n"
            + read_file("framework/BUILD_CONSTRAINTS.md"),
            "## Framework: Worksheet Types\n\n"
            + read_file("framework/WORKSHEET_TYPES.md"),
            f"## Child Profile: {child}\n\n" + read_file(f"profiles/{child}/PROFILE.md"),
        ]
    )


def media_type_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "application/pdf"
    if suffix == ".png":
        return "image/png"
    return "image/jpeg"


def strip_markdown_fences(raw_text: str) -> str:
    html = re.sub(r"^```html\s*", "", raw_text, flags=re.IGNORECASE)
    html = re.sub(r"^```\s*", "", html, flags=re.IGNORECASE)
    html = re.sub(r"\s*```$", "", html, flags=re.IGNORECASE)
    return html.strip()


def extract_text_blocks(response) -> str:
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )


def split_update_block(raw_text: str) -> tuple[str, str | None]:
    match = UPDATE_BLOCK_RE.search(raw_text)
    if not match:
        return raw_text, None
    body = match.group("body").strip()
    html_only = UPDATE_BLOCK_RE.sub("", raw_text).strip()
    return html_only, body


def append_pending_update(update_text: str, out_file: Path, worksheet_path: Path) -> None:
    PENDING_UPDATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PENDING_UPDATES_FILE.open("a", encoding="utf8") as f:
        f.write("\n\n---\n")
        f.write(f"Trigger Worksheet: {worksheet_path}\n")
        f.write(f"Generated Output: {out_file.relative_to(ROOT).as_posix()}\n\n")
        f.write(update_text)
        f.write("\n")


def today_iso() -> str:
    return date.today().isoformat()


def main() -> int:
    load_dotenv()
    args = parse_args()

    worksheet_path = Path(args.worksheet).expanduser().resolve()
    child = args.child
    date_str = args.date_str
    subject = args.subject

    system_prompt = assemble_system_prompt(child)
    worksheet_b64 = base64.b64encode(worksheet_path.read_bytes()).decode("ascii")
    media_type = media_type_for(worksheet_path)

    client = Anthropic()
    model_name = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-5")

    print(f"🔨 Building worksheet app for {child} — {subject} ({date_str})")
    print(f"📄 Worksheet: {worksheet_path}")

    response = client.messages.create(
        model=model_name,
        max_tokens=8096,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document" if media_type == "application/pdf" else "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": worksheet_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Build an accessible worksheet app for {child} from this worksheet. "
                            "Return exactly one HTML document starting with <!DOCTYPE html>. "
                            "Do not use markdown fences. "
                            "If no framework/profile updates are needed, output only the HTML document. "
                            "If updates are needed, append them after </html> in this exact wrapper: "
                            "<!-- COPILOT_UPDATE_SUGGESTED_START ... COPILOT_UPDATE_SUGGESTED_END -->. "
                            "Inside the wrapper, use the standard 📋 Update Suggested block format from CONTRIBUTING.md. "
                            "If the worksheet type is not represented in WORKSHEET_TYPES.md, include at least one "
                            "update suggestion targeting framework/WORKSHEET_TYPES.md inside that wrapper."
                        ),
                    },
                ],
            }
        ],
    )

    raw_text = extract_text_blocks(response)
    html_text, update_block = split_update_block(raw_text)
    html = strip_markdown_fences(html_text)

    if not html.lower().startswith("<!doctype"):
        print(
            f"❌ Response does not look like HTML. Raw output saved to {DEBUG_RESPONSE_FILE}",
            file=sys.stderr,
        )
        DEBUG_RESPONSE_FILE.parent.mkdir(parents=True, exist_ok=True)
        DEBUG_RESPONSE_FILE.write_text(raw_text, encoding="utf8")
        return 1

    out_dir = ROOT / "worksheets" / child
    out_file = out_dir / f"{date_str}-{subject}.html"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html, encoding="utf8")

    print(f"✅ Written: {out_file.relative_to(ROOT).as_posix()}")

    if update_block:
        append_pending_update(update_block, out_file, worksheet_path)
        print("\n📋 Captured framework/profile update suggestions.")
        print(f"📝 Appended to: {PENDING_UPDATES_FILE.relative_to(ROOT).as_posix()}")
        print("Run `python runners/propagate.py` to open a PR with these changes.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())