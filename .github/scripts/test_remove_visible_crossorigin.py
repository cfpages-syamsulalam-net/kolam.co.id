#!/usr/bin/env python3
"""Comprehensive test suite for remove_visible_crossorigin.py."""

import shutil
import tempfile
import unittest
from pathlib import Path
import sys

# Add script directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "canonical" / "scripts"))
import remove_visible_crossorigin as engine


class TestRemoveVisibleCrossOrigin(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.root = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_heal_corrupted_html_missing_head(self):
        corrupted = (
            '<!DOCTYPE html>\n'
            '<html lang="en-US" prefix="og: https://ogp.me/ns#">\n'
            '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3534718780470570" crossorigin="anonymous"></script>\n'
            '     crossorigin="anonymous"></script>\n'
            '<meta charset="UTF-8">\n'
            '<title>Sample Page</title>\n'
            '</head>\n'
            '<body>Content</body>\n'
            '</html>'
        )
        healed, changed, details = engine.heal_html(corrupted)
        self.assertTrue(changed)
        self.assertIn("restored_head_and_removed_stray_crossorigin", details)
        self.assertIn("<head>", healed)
        self.assertNotIn('     crossorigin="anonymous"></script>', healed)
        self.assertIn('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3534718780470570" crossorigin="anonymous"></script>', healed)

        # Idempotence: running again yields no changes
        healed2, changed2, _ = engine.heal_html(healed)
        self.assertFalse(changed2)
        self.assertEqual(healed, healed2)

    def test_heal_corrupted_crlf(self):
        corrupted = (
            '<!DOCTYPE html>\r\n'
            '<html lang="id">\r\n'
            '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1234567890123456" crossorigin="anonymous"></script>\r\n'
            'crossorigin="anonymous"></script>\r\n'
            '<meta charset="UTF-8">\r\n'
            '</head>\r\n'
            '<body>Test</body>\r\n'
            '</html>'
        )
        healed, changed, _ = engine.heal_html(corrupted)
        self.assertTrue(changed)
        self.assertIn("\r\n<head>\r\n", healed)
        self.assertEqual(healed.count('crossorigin="anonymous"></script>'), 1)

    def test_clean_html_untouched(self):
        clean = (
            '<!DOCTYPE html>\n'
            '<html>\n'
            '<head>\n'
            '<title>Clean Page</title>\n'
            '</head>\n'
            '<body>Hello World</body>\n'
            '</html>'
        )
        healed, changed, details = engine.heal_html(clean)
        self.assertFalse(changed)
        self.assertEqual(clean, healed)
        self.assertEqual(details, "unchanged")

    def test_file_processing_and_directory_run(self):
        file1 = self.root / "index.html"
        file1.write_text(
            '<!DOCTYPE html>\n'
            '<html>\n'
            '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3534718780470570" crossorigin="anonymous"></script>\n'
            '     crossorigin="anonymous"></script>\n'
            '</head><body>Home</body></html>',
            encoding="utf-8"
        )

        sub = self.root / "about"
        sub.mkdir()
        file2 = sub / "index.html"
        file2.write_text(
            '<!DOCTYPE html>\n<html><head><title>About</title></head><body>About</body></html>',
            encoding="utf-8"
        )

        summary = engine.run(self.root)
        self.assertEqual(summary["status"], "success")
        self.assertEqual(summary["scanned_html_files"], 2)
        self.assertEqual(summary["changed_files_count"], 1)
        self.assertEqual(summary["changed_files"][0]["path"], "index.html")

        # Verify file1 was repaired
        repaired_content = file1.read_text(encoding="utf-8")
        self.assertIn("<head>", repaired_content)
        self.assertEqual(repaired_content.count('crossorigin="anonymous"></script>'), 1)

        # Re-run for idempotence
        summary2 = engine.run(self.root)
        self.assertEqual(summary2["changed_files_count"], 0)


if __name__ == "__main__":
    unittest.main()
