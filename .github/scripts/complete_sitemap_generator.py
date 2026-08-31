from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import tempfile
import xml.etree.ElementTree as element_tree
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlsplit
from xml.sax.saxutils import escape as xml_escape


SITEMAP_PATH = "sitemap-complete.xml"
ALLOWED_OUTPUTS = (SITEMAP_PATH,)


@dataclass(frozen=True)
class TextStyle:
    bom: bool
    newline: str
    final_newline: bool


@dataclass(frozen=True)
class Page:
    relative_path: str
    url: str
    lastmod: str


def fail(message: str) -> None:
    raise SystemExit(message)


def git_result(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git_bytes(root: Path, *args: str) -> bytes:
    result = git_result(root, *args)
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", "replace").strip()
        fail(message or f"git {' '.join(args)} failed")
    return result.stdout


def parse_nonnegative_integer(value: str, name: str) -> int:
    if not value.isascii() or not value.isdigit():
        fail(f"{name} must be a nonnegative decimal integer")
    return int(value)


def normalize_origin(value: str, label: str) -> str:
    candidate = value.strip()
    parsed = urlsplit(candidate)
    try:
        port = parsed.port
    except ValueError as exc:
        fail(f"{label} has an invalid port: {exc}")
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        fail(f"{label} must be an HTTPS origin without credentials, port, path, query, or fragment")
    hostname = parsed.hostname.encode("idna").decode("ascii").lower()
    labels = hostname.split(".")
    if (
        len(labels) < 2
        or any(not item or len(item) > 63 for item in labels)
        or any(item.startswith("-") or item.endswith("-") for item in labels)
        or any(not re.fullmatch(r"[a-z0-9-]+", item) for item in labels)
    ):
        fail(f"{label} hostname is invalid")
    return f"https://{hostname}"


def is_tracked(root: Path, relative: str) -> bool:
    return git_result(root, "ls-files", "--error-unmatch", "--", relative).returncode == 0


def decode_document(data: bytes, label: str) -> tuple[str, TextStyle]:
    bom = data.startswith(b"\xef\xbb\xbf")
    payload = data[3:] if bom else data
    try:
        text = payload.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        fail(f"{label} is not strict UTF-8: {exc}")
    if "\r" in text.replace("\r\n", ""):
        fail(f"{label} contains unsupported bare carriage returns")
    has_crlf = "\r\n" in text
    has_lf = "\n" in text.replace("\r\n", "")
    if has_crlf and has_lf:
        fail(f"{label} contains mixed LF and CRLF newlines")
    normalized = text.replace("\r\n", "\n")
    return normalized, TextStyle(bom, "\r\n" if has_crlf else "\n", normalized.endswith("\n"))


def style_for(path: Path) -> TextStyle:
    if not path.exists():
        return TextStyle(False, "\n", True)
    if not path.is_file() or path.is_symlink():
        fail(f"output path is not a regular non-symlink file: {path.name}")
    _, style = decode_document(path.read_bytes(), path.name)
    return style


def encode_document(normalized: str, style: TextStyle) -> bytes:
    body = normalized.rstrip("\n") + ("\n" if style.final_newline else "")
    if style.newline == "\r\n":
        body = body.replace("\n", "\r\n")
    encoded = body.encode("utf-8")
    return (b"\xef\xbb\xbf" if style.bom else b"") + encoded


def resolve_base_url(root: Path, explicit: str, repository: str) -> str:
    if explicit.strip():
        return normalize_origin(explicit, "base_url")
    if is_tracked(root, "CNAME"):
        cname = root / "CNAME"
        if not cname.is_file() or cname.is_symlink():
            fail("tracked CNAME must be a regular non-symlink file")
        text, _ = decode_document(cname.read_bytes(), "CNAME")
        values = [line.strip() for line in text.split("\n") if line.strip()]
        if len(values) != 1 or any(char.isspace() for char in values[0]):
            fail("tracked CNAME must contain exactly one hostname")
        return normalize_origin(f"https://{values[0]}", "CNAME")
    parts = repository.split("/", 1)
    if len(parts) != 2 or not parts[1].strip():
        fail("repository must use OWNER/NAME form when base_url and tracked CNAME are absent")
    return normalize_origin(f"https://{parts[1].strip().lower()}", "repository name")


def tracked_html_paths(root: Path) -> list[str]:
    raw = git_bytes(root, "ls-files", "-z")
    paths: list[str] = []
    root_resolved = root.resolve()
    for item in raw.split(b"\0"):
        if not item:
            continue
        try:
            relative = item.decode("utf-8", "strict")
        except UnicodeDecodeError:
            fail("tracked path is not strict UTF-8")
        if not relative.casefold().endswith(".html"):
            continue
        if any(ord(char) < 32 or ord(char) == 127 for char in relative):
            fail(f"tracked HTML path contains a control character: {relative!r}")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or any(part in ("", ".", "..") for part in pure.parts):
            fail(f"unsafe tracked HTML path: {relative}")
        candidate = root / Path(*pure.parts)
        if candidate.is_symlink() or not candidate.is_file():
            fail(f"tracked HTML path is absent, non-file, or symlinked: {relative}")
        try:
            candidate.resolve().relative_to(root_resolved)
        except ValueError:
            fail(f"tracked HTML path escapes the repository: {relative}")
        paths.append(relative)
    ordered = sorted(paths, key=lambda item: item.encode("utf-8"))
    if len(ordered) != len(set(ordered)):
        fail("tracked HTML path list contains duplicates")
    casefolded: dict[str, str] = {}
    for relative in ordered:
        folded = relative.casefold()
        if folded in casefolded:
            fail(f"tracked HTML paths collide by case: {casefolded[folded]!r} and {relative!r}")
        casefolded[folded] = relative
    return ordered


def git_lastmod_map(root: Path, tracked: list[str]) -> dict[str, str]:
    output = git_bytes(
        root,
        "-c",
        "core.quotepath=false",
        "log",
        "--format=%x1e%cI",
        "--name-only",
        "--no-renames",
        "--",
    )
    wanted = set(tracked)
    found: dict[str, str] = {}
    for record in output.decode("utf-8", "strict").split("\x1e"):
        if not record.strip():
            continue
        lines = record.lstrip("\n").splitlines()
        if not lines:
            continue
        try:
            instant = datetime.fromisoformat(lines[0].strip())
        except ValueError:
            fail(f"Git returned an invalid commit timestamp: {lines[0]!r}")
        if instant.tzinfo is None:
            fail("Git returned a commit timestamp without a timezone")
        lastmod = instant.astimezone(timezone.utc).isoformat(timespec="seconds")
        for relative in lines[1:]:
            if relative in wanted and relative not in found:
                found[relative] = lastmod
        if len(found) == len(wanted):
            break
    missing = sorted(wanted.difference(found), key=lambda item: item.encode("utf-8"))
    if missing:
        fail(f"Git history does not provide lastmod evidence for {len(missing)} tracked HTML paths")
    return found


def route_for(relative: str) -> str:
    pure = PurePosixPath(relative)
    if pure.name.casefold() == "index.html":
        route_parts = pure.parts[:-1]
        suffix = "/"
    else:
        route_parts = (*pure.parts[:-1], pure.name[:-5])
        suffix = ""
    encoded = "/".join(quote(part, safe="-._~") for part in route_parts)
    return "/" if not encoded else f"/{encoded}{suffix}"


def build_pages(root: Path, base_url: str, minimum_urls: int) -> list[Page]:
    paths = tracked_html_paths(root)
    if len(paths) < minimum_urls:
        fail(f"tracked HTML URL count {len(paths)} is below required minimum {minimum_urls}")
    if not paths:
        fail("no tracked HTML files were found")
    lastmods = git_lastmod_map(root, paths)
    pages = [Page(path, base_url + route_for(path), lastmods[path]) for path in paths]
    urls = [page.url for page in pages]
    if len(urls) != len(set(urls)):
        duplicates = sorted({url for url in urls if urls.count(url) > 1})
        fail("multiple tracked HTML paths map to the same URL: " + json.dumps(duplicates, ensure_ascii=False))
    return sorted(pages, key=lambda page: page.url.encode("utf-8"))


def render_sitemap(pages: list[Page]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in pages:
        lines.extend(
            (
                "  <url>",
                f"    <loc>{xml_escape(page.url)}</loc>",
                f"    <lastmod>{page.lastmod}</lastmod>",
                "    <priority>0.80</priority>",
                "  </url>",
            )
        )
    lines.append("</urlset>")
    return "\n".join(lines)


def atomic_replace(path: Path, data: bytes) -> None:
    if path.exists() and (not path.is_file() or path.is_symlink()):
        fail(f"output path is not a regular non-symlink file: {path.name}")
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_new(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def publish_controls(paths_file: Path, summary_file: Path, github_output: Path, changed: list[str], summary: dict[str, object]) -> None:
    write_new(paths_file, b"".join(path.encode("utf-8") + b"\0" for path in changed))
    write_new(
        summary_file,
        (json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"),
    )
    with github_output.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"changed={'true' if changed else 'false'}\n")
        stream.write(f"changed_files={len(changed)}\n")
        stream.write(f"url_count={summary['url_count']}\n")


def generate(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not (root / ".git").is_dir():
        fail("root must be a Git checkout")
    minimum_urls = parse_nonnegative_integer(args.minimum_urls, "minimum_urls")
    base_url = resolve_base_url(root, args.base_url, args.repository)
    pages = build_pages(root, base_url, minimum_urls)
    output = root / SITEMAP_PATH
    style = style_for(output)
    desired = encode_document(render_sitemap(pages), style)
    try:
        parsed = element_tree.fromstring(desired)
    except element_tree.ParseError as exc:
        fail(f"generated sitemap is not valid XML: {exc}")
    if parsed.tag != "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset":
        fail("generated sitemap has an unexpected root element")
    original = output.read_bytes() if output.exists() else None
    changed = [SITEMAP_PATH] if original != desired else []
    if changed:
        atomic_replace(output, desired)
    summary: dict[str, object] = {
        "schema_version": "complete-sitemap-generation-summary-v1",
        "base_url": base_url,
        "url_count": len(pages),
        "changed_files": changed,
    }
    publish_controls(
        Path(args.paths_file).resolve(),
        Path(args.summary_file).resolve(),
        Path(args.github_output).resolve(),
        changed,
        summary,
    )
    print(json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    return 0


def read_paths_file(path: Path) -> list[str]:
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\0"):
        fail("paths file is not NUL terminated")
    paths: list[str] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        try:
            relative = item.decode("utf-8", "strict")
        except UnicodeDecodeError:
            fail("paths file contains non-UTF-8 bytes")
        if relative not in ALLOWED_OUTPUTS:
            fail(f"unsafe output path in paths file: {relative}")
        paths.append(relative)
    if paths != sorted(set(paths), key=lambda item: item.encode("utf-8")):
        fail("paths file must be unique and bytewise sorted")
    return paths


def porcelain(root: Path) -> dict[str, str]:
    records = git_bytes(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0")
    result: dict[str, str] = {}
    for record in records:
        if not record:
            continue
        if len(record) < 4 or record[2:3] != b" ":
            fail("unsupported porcelain record")
        status_code = record[:2].decode("ascii", "strict")
        if "R" in status_code or "C" in status_code:
            fail("rename/copy status is outside the generation contract")
        relative = record[3:].decode("utf-8", "strict")
        if relative in result:
            fail(f"duplicate porcelain path: {relative}")
        result[relative] = status_code
    return result


def verify_git(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    expected = read_paths_file(Path(args.paths_file).resolve())
    actual = porcelain(root)
    if sorted(actual, key=lambda item: item.encode("utf-8")) != expected:
        fail("Git path boundary mismatch: " + json.dumps({"expected": expected, "actual": sorted(actual)}, separators=(",", ":")))
    allowed = {" M", "??"} if args.state == "unstaged" else {"M ", "A "}
    bad = {path: actual[path] for path in expected if actual[path] not in allowed}
    if bad:
        fail(f"unexpected Git status for {args.state}: {json.dumps(bad, separators=(',', ':'))}")
    print(json.dumps({"status": "pass", "state": args.state, "paths": len(expected)}, separators=(",", ":")))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    generator = commands.add_parser("generate")
    generator.add_argument("--root", required=True)
    generator.add_argument("--repository", required=True)
    generator.add_argument("--base-url", default="")
    generator.add_argument("--minimum-urls", required=True)
    generator.add_argument("--paths-file", required=True)
    generator.add_argument("--summary-file", required=True)
    generator.add_argument("--github-output", required=True)
    verifier = commands.add_parser("verify-git")
    verifier.add_argument("--root", required=True)
    verifier.add_argument("--paths-file", required=True)
    verifier.add_argument("--state", required=True, choices=("unstaged", "staged"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return generate(args) if args.command == "generate" else verify_git(args)


if __name__ == "__main__":
    raise SystemExit(main())
