#!/usr/bin/env python3
"""Framework update propagation runner."""

from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List

import requests
from anthropic import Anthropic
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent


@dataclass
class UpdateBlock:
    file: str
    change: str
    raw: str


def extract_heading(chunk: str) -> str:
    for line in chunk.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("**File:**"):
            break
        stripped = stripped.lstrip("#*- ").strip()
        if stripped:
            return stripped
    return ""


def summarize_change(chunk: str, file_path: str) -> str:
    change_match = re.search(
        r"\*\*Change:\*\*\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)",
        chunk,
        flags=re.IGNORECASE,
    )
    if change_match:
        return change_match.group(1).strip()

    heading = extract_heading(chunk)
    if heading:
        heading = re.sub(
            r"^(?:Framework|Profile|Baseline Spec|Constitution) Update\s*[—-]\s*",
            "",
            heading,
            flags=re.IGNORECASE,
        ).strip()
        if heading:
            return heading

    section_match = re.search(r"\*\*Section:\*\*\s*([^\n]+)", chunk, flags=re.IGNORECASE)
    if section_match:
        return section_match.group(1).strip()

    return f"Update {file_path}"


def today_iso() -> str:
    return date.today().isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply pending framework updates and open GitHub PRs.")
    parser.add_argument("update_file", nargs="?", help="Optional markdown file containing update blocks")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_input(args: argparse.Namespace) -> tuple[str, str]:
    if not sys.stdin.isatty():
        return sys.stdin.read(), "stdin"

    if args.update_file:
        file_path = Path(args.update_file).expanduser().resolve()
        return file_path.read_text(encoding="utf8"), "file"

    pending_file = ROOT / "pending-updates.md"
    if not pending_file.exists():
        print("No pending-updates.md found. Nothing to propagate.")
        raise SystemExit(0)

    return pending_file.read_text(encoding="utf8"), "pending"


def parse_update_blocks(text: str) -> List[UpdateBlock]:
    blocks: List[UpdateBlock] = []
    for chunk in [part for part in text.split("📋") if part.strip()]:
        file_match = re.search(r"\*\*File:\*\*\s*`?([^\n`]+)`?", chunk, flags=re.IGNORECASE)
        if file_match:
            blocks.append(
                UpdateBlock(
                    file=file_match.group(1).strip(),
                    change=summarize_change(chunk, file_match.group(1).strip()),
                    raw="📋" + chunk.strip(),
                )
            )
    return blocks


def extract_text_blocks(response) -> str:
    return "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    ).strip()


def apply_update(client: Anthropic, model_name: str, current_content: str, block: UpdateBlock) -> str:
    response = client.messages.create(
        model=model_name,
        max_tokens=8096,
        messages=[
            {
                "role": "user",
                "content": (
                    "You are updating a framework documentation file for an accessible worksheet app builder.\n\n"
                    "Current file content:\n"
                    "```markdown\n"
                    f"{current_content}\n"
                    "```\n\n"
                    "Apply this change:\n"
                    f"{block.raw}\n\n"
                    "Rules:\n"
                    "- Output only the complete updated file content — no explanation, no markdown fences\n"
                    "- Preserve all existing content that is not affected by this change\n"
                    "- Integrate the change naturally into the existing structure\n"
                    "- Do not add new sections unless the change explicitly requires it"
                ),
            }
        ],
    )
    return extract_text_blocks(response)


class GitHubClient:
    def __init__(self, token: str, owner: str, repo: str) -> None:
        self.owner = owner
        self.repo = repo
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def request(self, method: str, path: str, **kwargs):
        response = self.session.request(
            method,
            f"https://api.github.com/repos/{self.owner}/{self.repo}{path}",
            timeout=30,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()

    def get_main_sha(self) -> str:
        data = self.request("GET", "/git/ref/heads/main")
        return data["object"]["sha"]

    def create_branch(self, branch_name: str, sha: str) -> None:
        self.request("POST", "/git/refs", json={"ref": f"refs/heads/{branch_name}", "sha": sha})

    def get_file_sha(self, repo_file_path: str) -> str:
        data = self.request("GET", f"/contents/{repo_file_path}")
        return data["sha"]

    def update_file(self, repo_file_path: str, new_content: str, branch_name: str, block: UpdateBlock) -> None:
        sha = self.get_file_sha(repo_file_path)
        content_b64 = base64.b64encode(new_content.encode("utf8")).decode("ascii")
        self.request(
            "PUT",
            f"/contents/{repo_file_path}",
            json={
                "message": f"Update {repo_file_path}: {block.change[:72]}",
                "content": content_b64,
                "sha": sha,
                "branch": branch_name,
            },
        )

    def create_pull_request(self, branch_name: str, block: UpdateBlock) -> str:
        data = self.request(
            "POST",
            "/pulls",
            json={
                "title": f"Framework update: {block.change[:72]}",
                "body": f"## Automated framework update\n\n{block.raw}\n\n---\n*Opened by propagate.py*",
                "head": branch_name,
                "base": "main",
            },
        )
        return data["html_url"]


def show_diff(before: str, after: str) -> None:
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    shown = 0

    for index in range(max(len(before_lines), len(after_lines))):
        left = before_lines[index] if index < len(before_lines) else None
        right = after_lines[index] if index < len(after_lines) else None
        if left != right:
            if left is not None:
                print(f"   - {left}")
            if right is not None:
                print(f"   + {right}")
            shown += 1
            if shown >= 5:
                break


def slugify(text: str) -> str:
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", text[:40].lower()))


def main() -> int:
    load_dotenv()
    args = parse_args()
    input_text, input_source = read_input(args)
    update_blocks = parse_update_blocks(input_text)

    if not update_blocks:
        print("No update blocks found.")
        return 0

    print(f"Found {len(update_blocks)} update block(s).")
    if args.dry_run:
        print("DRY RUN — no commits or PRs will be created.\n")

    model_name = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-5")
    client = Anthropic()

    owner = repo = ""
    github = None
    if not args.dry_run:
        owner, repo = (os.environ.get("GITHUB_REPO", "") or "").split("/", 1) if "/" in os.environ.get("GITHUB_REPO", "") else ("", "")
        if not owner or not repo:
            print("Set GITHUB_REPO=owner/repo-name in your environment", file=sys.stderr)
            return 1
        token = os.environ.get("GITHUB_TOKEN", "")
        github = GitHubClient(token, owner, repo)

    for block in update_blocks:
        print(f"\n📋 Processing: {block.file}")
        print(f"   Change: {block.change[:80]}...")

        file_path = ROOT / block.file
        if not file_path.exists():
            print(f"   ⚠️  File not found: {block.file} — skipping")
            continue

        current_content = file_path.read_text(encoding="utf8")
        updated_content = apply_update(client, model_name, current_content, block)

        if args.dry_run:
            print(f"   Would update: {block.file}")
            print("   Preview (first 200 chars of diff):")
            show_diff(current_content, updated_content)
            continue

        branch_name = f"update/{slugify(block.change)}-{today_iso()}"
        assert github is not None
        base_sha = github.get_main_sha()
        github.create_branch(branch_name, base_sha)
        github.update_file(block.file, updated_content, branch_name, block)
        pr_url = github.create_pull_request(branch_name, block)
        print(f"   ✅ PR opened: {pr_url}")

    if not args.dry_run and input_source == "pending":
        (ROOT / "pending-updates.md").write_text("", encoding="utf8")
        print("\n✅ Cleared pending-updates.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())