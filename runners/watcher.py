#!/usr/bin/env python3
"""Automatic worksheet processor."""

from __future__ import annotations

import base64
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import date
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


ROOT = Path(__file__).resolve().parent.parent
VALID_SUFFIXES = {".pdf", ".jpg", ".jpeg", ".png"}


def today_iso() -> str:
    return date.today().isoformat()


def read_framework_file(rel_path: str) -> str:
    full_path = ROOT / rel_path
    if not full_path.exists():
        print(f"⚠️  Missing: {rel_path}", file=sys.stderr)
        return ""
    return full_path.read_text(encoding="utf8")


def assemble_system_prompt(child: str) -> str:
    return "\n\n".join(
        [
            read_framework_file("SYSTEM_PROMPT.md"),
            "---",
            "## Framework: Design System\n\n"
            + read_framework_file("framework/DESIGN_SYSTEM.md"),
            "## Framework: Interaction Patterns\n\n"
            + read_framework_file("framework/INTERACTION_PATTERNS.md"),
            "## Framework: Build Constraints\n\n"
            + read_framework_file("framework/BUILD_CONSTRAINTS.md"),
            "## Framework: Worksheet Types\n\n"
            + read_framework_file("framework/WORKSHEET_TYPES.md"),
            f"## Child Profile: {child}\n\n"
            + read_framework_file(f"profiles/{child}/PROFILE.md"),
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


def wait_for_stable_file(path: Path, debounce_seconds: float) -> None:
    stable_checks = 0
    previous_size = -1

    while stable_checks < 2:
        if not path.exists():
            raise FileNotFoundError(path)

        current_size = path.stat().st_size
        if current_size == previous_size:
            stable_checks += 1
        else:
            stable_checks = 0
            previous_size = current_size

        time.sleep(debounce_seconds)


def commit_and_push(root: Path, out_file: Path, date_str: str, subject: str) -> None:
    rel_path = out_file.relative_to(root).as_posix()
    commands = [
        ["git", "-C", str(root), "add", rel_path],
        ["git", "-C", str(root), "commit", "-m", f"Add worksheet: {date_str} {subject}"],
        ["git", "-C", str(root), "push"],
    ]

    try:
        for command in commands:
            subprocess.run(command, check=True, capture_output=True, text=True)
        print("🚀 Committed and pushed")
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() or error.stdout.strip() or str(error)
        print(f"⚠️  Git commit failed: {message}", file=sys.stderr)


class WorksheetProcessor:
    def __init__(self) -> None:
        load_dotenv()
        self.config = {
            "incoming_dir": Path(os.environ.get("INCOMING_DIR", ROOT / "incoming")).expanduser().resolve(),
            "output_dir": Path(os.environ.get("OUTPUT_DIR", ROOT / "worksheets")).expanduser().resolve(),
            "child": os.environ.get("CHILD", "christina"),
            "auto_commit": os.environ.get("AUTO_COMMIT") == "true",
            "debounce_seconds": 2.0,
            "model": os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-5"),
        }
        self.client = Anthropic()
        self.processing = set()
        self.lock = threading.Lock()

    def bootstrap(self) -> None:
        self.config["incoming_dir"].mkdir(parents=True, exist_ok=True)
        self.config["output_dir"].mkdir(parents=True, exist_ok=True)

        print(f"👀 Watching: {self.config['incoming_dir']}")
        print(f"📁 Output:   {self.config['output_dir']}")
        print(f"👤 Child:    {self.config['child']}")
        if self.config["auto_commit"]:
            print("🚀 Auto-commit: enabled")

        self.process_existing_files()
        self.watch_for_changes()

    def process_existing_files(self) -> None:
        for path in sorted(self.config["incoming_dir"].iterdir()):
            if path.is_file() and path.suffix.lower() in VALID_SUFFIXES:
                self.handle_candidate(path)

    def watch_for_changes(self) -> None:
        observer = Observer()
        observer.schedule(WorksheetEventHandler(self), str(self.config["incoming_dir"]), recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def handle_candidate(self, path: Path) -> None:
        resolved = path.resolve()
        if resolved.suffix.lower() not in VALID_SUFFIXES:
            return

        with self.lock:
            if resolved in self.processing:
                return
            self.processing.add(resolved)

        threading.Thread(target=self._process_in_background, args=(resolved,), daemon=True).start()

    def _process_in_background(self, worksheet_path: Path) -> None:
        try:
            wait_for_stable_file(worksheet_path, self.config["debounce_seconds"])
            self.process_worksheet(worksheet_path)
        except Exception as error:
            print(f"❌ Failed to process {worksheet_path.name}: {error}", file=sys.stderr)
        finally:
            with self.lock:
                self.processing.discard(worksheet_path)

    def process_worksheet(self, worksheet_path: Path) -> None:
        basename = worksheet_path.stem
        print(f"\n📄 Processing: {basename}")

        match = re.match(r"^(\d{4}-\d{2}-\d{2})-?(.+)?$", basename)
        date_str = match.group(1) if match else today_iso()
        if match and match.group(2):
            subject = re.sub(r"[^a-z0-9-]", "-", match.group(2), flags=re.IGNORECASE).lower()
        else:
            subject = "worksheet"

        system_prompt = assemble_system_prompt(self.config["child"])
        worksheet_b64 = base64.b64encode(worksheet_path.read_bytes()).decode("ascii")
        media_type = media_type_for(worksheet_path)

        print("🔨 Generating app...")
        response = self.client.messages.create(
            model=self.config["model"],
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
                                f"Build an accessible worksheet app for {self.config['child']} from this worksheet. "
                                "Output only the complete HTML file — no explanation, no markdown fences, "
                                "just the raw HTML starting with <!DOCTYPE html>."
                            ),
                        },
                    ],
                }
            ],
        )

        raw_text = extract_text_blocks(response)
        html = strip_markdown_fences(raw_text)
        if not html.lower().startswith("<!doctype"):
            raise ValueError("Response does not look like HTML")

        child_out_dir = self.config["output_dir"] / self.config["child"]
        out_file = child_out_dir / f"{date_str}-{subject}.html"
        child_out_dir.mkdir(parents=True, exist_ok=True)
        out_file.write_text(html, encoding="utf8")
        print(f"✅ Written: {out_file.relative_to(ROOT).as_posix()}")

        if "📋" in raw_text:
            update_block = "".join("📋" + chunk for chunk in raw_text.split("📋")[1:])
            suggestions_file = ROOT / "pending-updates.md"
            with suggestions_file.open("a", encoding="utf8") as handle:
                handle.write(f"\n\n<!-- From {basename} on {today_iso()} -->\n{update_block}")
            print("📋 Update suggestions saved to pending-updates.md")

        if self.config["auto_commit"]:
            commit_and_push(ROOT, out_file, date_str, subject)

        done_dir = self.config["incoming_dir"] / "done"
        done_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(worksheet_path), done_dir / worksheet_path.name)
        print("📦 Moved worksheet to incoming/done/")


class WorksheetEventHandler(FileSystemEventHandler):
    def __init__(self, processor: WorksheetProcessor) -> None:
        super().__init__()
        self.processor = processor

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self.processor.handle_candidate(Path(event.src_path))

    def on_moved(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self.processor.handle_candidate(Path(event.dest_path))


def main() -> int:
    WorksheetProcessor().bootstrap()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())