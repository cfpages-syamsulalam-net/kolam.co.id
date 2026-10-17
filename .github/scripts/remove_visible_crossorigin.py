#!/usr/bin/env python3
"""Canonical Engine: Remove Visible Crossorigin Defect & Restore Missing Head Tag.

Heals HTML files corrupted by legacy AdSense scripts where:
1. The opening <head> tag was stripped.
2. A duplicate/stray 'crossorigin="anonymous"></script>' was injected,
   rendering 'crossorigin="anonymous">' as visible text at the top of web pages.

This script:
- Re-inserts the proper <head> tag right after <html...>.
- Preserves the canonical AdSense script inside <head>.
- Eliminates the stray 'crossorigin="anonymous"></script>'.
- Preserves exact document encoding (strict UTF-8 / BOM) and newline conventions (CRLF vs LF).
- Is 100% idempotent.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path


# Regex matching the corrupted header sequence
CORRUPTED_PATTERN = re.compile(
    r'(<html\b[^>]*>)\s*'
    r'(<script\s+async\s+src="[^"]*pagead2[^"]*"[^>]*></script>)\s*'
    r'crossorigin="anonymous"></script>',
    re.IGNORECASE
)

# Regex matching stray standalone lines of the duplicate closing tag
STRAY_LINE_PATTERN = re.compile(
    r'^[ \t]*crossorigin="anonymous"></script>[ \t]*\r?\n?',
    re.IGNORECASE | re.MULTILINE
)


@dataclass(frozen=True)
class ProcessResult:
    path: Path
    relative: str
    changed: bool
    details: str


def heal_html(content: str) -> tuple[str, bool, str]:
    """Heal the corrupted HTML content idempotently."""
    changed = False
    details = []

    newline = "\r\n" if "\r\n" in content[:400] else "\n"

    # Pattern 1: Exact corrupted block where <head> was stripped and stray line left
    if CORRUPTED_PATTERN.search(content):
        def replacer(match: re.Match) -> str:
            html_tag = match.group(1)
            script_tag = match.group(2)
            return f"{html_tag}{newline}<head>{newline}{script_tag}"

        content = CORRUPTED_PATTERN.sub(replacer, content, count=1)
        changed = True
        details.append("restored_head_and_removed_stray_crossorigin")

    # Pattern 2: Any residual standalone stray lines
    if STRAY_LINE_PATTERN.search(content):
        content = STRAY_LINE_PATTERN.sub("", content)
        changed = True
        details.append("removed_residual_stray_lines")

    # Safety check: if </head> exists but <head> is missing, insert <head> after <html...>
    if "</head>" in content.lower() and "<head>" not in content.lower() and "<head " not in content.lower():
        html_match = re.search(r'<html\b[^>]*>', content, re.IGNORECASE)
        if html_match:
            idx = html_match.end()
            content = content[:idx] + f"{newline}<head>" + content[idx:]
            changed = True
            details.append("restored_missing_opening_head")

    return content, changed, ", ".join(details) if details else "unchanged"


def process_file(path: Path, root: Path) -> ProcessResult:
    rel_path = path.relative_to(root).as_posix()
    try:
        raw_bytes = path.read_bytes()
    except Exception as e:
        return ProcessResult(path, rel_path, False, f"read_error: {e}")

    bom = raw_bytes.startswith(b"\xef\xbb\xbf")
    payload = raw_bytes[3:] if bom else raw_bytes

    try:
        text = payload.decode("utf-8", "strict")
    except UnicodeDecodeError:
        try:
            text = payload.decode("latin-1")
        except Exception as e:
            return ProcessResult(path, rel_path, False, f"decode_error: {e}")

    healed_text, changed, detail = heal_html(text)

    if not changed:
        return ProcessResult(path, rel_path, False, "clean")

    out_bytes = (b"\xef\xbb\xbf" if bom else b"") + healed_text.encode("utf-8")

    # Atomic write
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".tmp_{path.name}_")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(out_bytes)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    return ProcessResult(path, rel_path, True, detail)


def run(root_dir: Path) -> dict:
    root = root_dir.resolve()
    scanned = 0
    changed_files = []

    ignore_dirs = {".git", "node_modules", "wp-content", "wp-includes", "dist", "build", ".next", ".cache", "vendor"}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for f in filenames:
            if f.lower().endswith(".html"):
                scanned += 1
                fp = Path(dirpath) / f
                res = process_file(fp, root)
                if res.changed:
                    changed_files.append({"path": res.relative, "detail": res.details})

    summary = {
        "status": "success",
        "scanned_html_files": scanned,
        "changed_files_count": len(changed_files),
        "changed_files": changed_files
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description="Remove visible crossorigin defect & restore head tag")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Root directory of repository")
    args = parser.parse_args()

    summary = run(args.root)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
