from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as element_tree
from argparse import Namespace
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().with_name("complete_sitemap_generator.py")
if not MODULE_PATH.exists():
    MODULE_PATH = Path(__file__).resolve().parents[1] / "canonical" / "scripts" / "complete_sitemap_generator.py"
SPEC = importlib.util.spec_from_file_location("complete_sitemap_generator", MODULE_PATH)
assert SPEC and SPEC.loader
GENERATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GENERATOR
SPEC.loader.exec_module(GENERATOR)


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


class CompleteSitemapGeneratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init")
        git(self.root, "config", "user.name", "Fixture")
        git(self.root, "config", "user.email", "fixture@example.invalid")
        self.controls: list[Path] = []

    def tearDown(self) -> None:
        for path in self.controls:
            if path.exists():
                path.unlink()
        self.temporary.cleanup()

    def write(self, relative: str, data: bytes) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def commit(self, message: str = "fixture") -> None:
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", message)

    def args(self, *, base_url: str = "", minimum_urls: str = "1", suffix: str = "one") -> Namespace:
        paths = self.root.parent / f"{self.root.name}-{suffix}-paths.nul"
        summary = self.root.parent / f"{self.root.name}-{suffix}-summary.json"
        output = self.root.parent / f"{self.root.name}-{suffix}-output.txt"
        self.controls.extend((paths, summary, output))
        return Namespace(
            root=str(self.root),
            repository="owner/Example.CO.ID",
            base_url=base_url,
            minimum_urls=minimum_urls,
            paths_file=str(paths),
            summary_file=str(summary),
            github_output=str(output),
        )

    def test_base_url_precedence_and_validation(self) -> None:
        self.write("index.html", b"home")
        self.commit()
        self.assertEqual(
            GENERATOR.resolve_base_url(self.root, "https://Explicit.ID", "owner/repo.id"),
            "https://explicit.id",
        )
        self.write("CNAME", b"Custom.Example.ID\n")
        git(self.root, "add", "CNAME")
        git(self.root, "commit", "-m", "cname")
        self.assertEqual(GENERATOR.resolve_base_url(self.root, "", "owner/repo.id"), "https://custom.example.id")
        (self.root / "CNAME").unlink()
        git(self.root, "rm", "--cached", "CNAME")
        self.assertEqual(
            GENERATOR.resolve_base_url(self.root, "", "owner/Example.CO.ID"),
            "https://example.co.id",
        )
        for value in (
            "http://example.id",
            "https://user@example.id",
            "https://example.id:443",
            "https://example.id/path",
            "https://example.id?q=1",
            "https://example.id/#x",
        ):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                GENERATOR.normalize_origin(value, "fixture")

    def test_generates_only_encoded_sorted_complete_sitemap(self) -> None:
        self.write("index.html", b"root")
        self.write("Folder Name/index.html", b"folder")
        self.write("produk/a & ñ.html", b"unicode")
        self.write("untracked.html", b"ignore")
        git(self.root, "add", "index.html", "Folder Name/index.html", "produk/a & ñ.html")
        git(self.root, "commit", "-m", "pages")
        args = self.args()
        GENERATOR.generate(args)
        sitemap = (self.root / GENERATOR.SITEMAP_PATH).read_text(encoding="utf-8")
        self.assertIn("<loc>https://example.co.id/</loc>", sitemap)
        self.assertIn("<loc>https://example.co.id/Folder%20Name/</loc>", sitemap)
        self.assertIn("<loc>https://example.co.id/produk/a%20%26%20%C3%B1</loc>", sitemap)
        self.assertNotIn("untracked", sitemap)
        self.assertEqual(sitemap.count("<url>"), 3)
        self.assertFalse((self.root / "README.md").exists())
        self.assertFalse((self.root / "url-list.txt").exists())
        self.assertEqual(Path(args.paths_file).read_bytes(), b"sitemap-complete.xml\0")
        summary = json.loads(Path(args.summary_file).read_text(encoding="utf-8"))
        self.assertEqual(summary["changed_files"], ["sitemap-complete.xml"])

    def test_output_is_valid_xml_and_escapes_locations(self) -> None:
        rendered = GENERATOR.render_sitemap(
            [GENERATOR.Page("fixture.html", "https://example.id/a?x=1&y=2", "2026-01-01T00:00:00+00:00")]
        )
        self.assertIn("x=1&amp;y=2", rendered)
        parsed = element_tree.fromstring(rendered.encode("utf-8"))
        self.assertEqual(parsed.tag, "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")

    def test_preserves_bom_crlf_and_final_newline_state(self) -> None:
        self.write("index.html", b"root")
        self.write(
            GENERATOR.SITEMAP_PATH,
            b"\xef\xbb\xbf<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<urlset></urlset>",
        )
        self.commit()
        GENERATOR.generate(self.args())
        data = (self.root / GENERATOR.SITEMAP_PATH).read_bytes()
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
        self.assertFalse(data.endswith(b"\r\n"))

    def test_second_run_is_idempotent_and_git_dates_stay_stable(self) -> None:
        self.write("index.html", b"root")
        self.write("nested/page.html", b"page")
        self.commit()
        first = self.args()
        GENERATOR.generate(first)
        original = (self.root / GENERATOR.SITEMAP_PATH).read_bytes()
        git(self.root, "add", GENERATOR.SITEMAP_PATH)
        git(self.root, "commit", "-m", "generated output")
        second = self.args(suffix="second")
        GENERATOR.generate(second)
        self.assertEqual(Path(second.paths_file).read_bytes(), b"")
        self.assertEqual((self.root / GENERATOR.SITEMAP_PATH).read_bytes(), original)
        self.assertEqual(git(self.root, "status", "--porcelain=v1"), b"?? untracked.html\n" if (self.root / "untracked.html").exists() else b"")

    def test_minimum_empty_duplicate_and_case_collision_poisons(self) -> None:
        self.write("page.html", b"page")
        self.commit()
        with self.assertRaises(SystemExit):
            GENERATOR.generate(self.args(minimum_urls="2"))
        with mock.patch.object(GENERATOR, "tracked_html_paths", return_value=["index.html", "INDEX.HTML"]):
            with mock.patch.object(
                GENERATOR,
                "git_lastmod_map",
                return_value={"index.html": "2026-01-01T00:00:00+00:00", "INDEX.HTML": "2026-01-01T00:00:00+00:00"},
            ):
                with self.assertRaises(SystemExit):
                    GENERATOR.build_pages(self.root, "https://example.id", 1)
        with mock.patch.object(GENERATOR, "git_bytes", return_value=b"A.html\0a.HTML\0"):
            with self.assertRaises(SystemExit):
                GENERATOR.tracked_html_paths(self.root)

        empty = tempfile.TemporaryDirectory()
        try:
            other = Path(empty.name)
            git(other, "init")
            git(other, "config", "user.name", "Fixture")
            git(other, "config", "user.email", "fixture@example.invalid")
            (other / "file.txt").write_text("x", encoding="utf-8")
            git(other, "add", ".")
            git(other, "commit", "-m", "empty")
            with self.assertRaises(SystemExit):
                GENERATOR.build_pages(other, "https://example.id", 0)
        finally:
            empty.cleanup()

    def test_invalid_utf8_cname_and_output_fail_before_mutation(self) -> None:
        self.write("index.html", b"root")
        self.write(GENERATOR.SITEMAP_PATH, b"\xff")
        self.commit()
        with self.assertRaises(SystemExit):
            GENERATOR.generate(self.args())
        self.assertEqual((self.root / GENERATOR.SITEMAP_PATH).read_bytes(), b"\xff")

        (self.root / GENERATOR.SITEMAP_PATH).unlink()
        self.write("CNAME", b"one.id\ntwo.id\n")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-m", "bad cname")
        with self.assertRaises(SystemExit):
            GENERATOR.generate(self.args(suffix="cname"))
        self.assertFalse((self.root / GENERATOR.SITEMAP_PATH).exists())

    def test_exact_git_boundary_before_and_after_staging(self) -> None:
        self.write("index.html", b"root")
        self.commit()
        args = self.args()
        GENERATOR.generate(args)
        GENERATOR.verify_git(Namespace(root=str(self.root), paths_file=args.paths_file, state="unstaged"))
        git(self.root, "add", "--pathspec-from-file=" + args.paths_file, "--pathspec-file-nul")
        GENERATOR.verify_git(Namespace(root=str(self.root), paths_file=args.paths_file, state="staged"))

    def test_unexpected_dirty_path_is_rejected(self) -> None:
        self.write("index.html", b"root")
        self.write("other.txt", b"clean\n")
        self.commit()
        args = self.args()
        GENERATOR.generate(args)
        self.write("other.txt", b"dirty\n")
        with self.assertRaises(SystemExit):
            GENERATOR.verify_git(Namespace(root=str(self.root), paths_file=args.paths_file, state="unstaged"))

    def test_symlinked_html_and_output_are_rejected(self) -> None:
        target = self.write("target.html", b"target")
        try:
            os.symlink(target, self.root / "linked.html")
        except OSError:
            self.skipTest("symlink creation is unavailable on this Windows host")
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "linked page")
        with self.assertRaises(SystemExit):
            GENERATOR.tracked_html_paths(self.root)

        (self.root / "linked.html").unlink()
        git(self.root, "rm", "linked.html")
        git(self.root, "commit", "-m", "remove link")
        os.symlink(target, self.root / GENERATOR.SITEMAP_PATH)
        with self.assertRaises(SystemExit):
            GENERATOR.generate(self.args(suffix="output-link"))

    def test_paths_control_file_rejects_noncanonical_or_duplicate_paths(self) -> None:
        control = self.root.parent / f"{self.root.name}-bad-paths.nul"
        self.controls.append(control)
        for data in (b"README.md\0", b"sitemap-complete.xml\0sitemap-complete.xml\0", b"sitemap-complete.xml"):
            control.write_bytes(data)
            with self.subTest(data=data), self.assertRaises(SystemExit):
                GENERATOR.read_paths_file(control)


if __name__ == "__main__":
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    unittest.main()
