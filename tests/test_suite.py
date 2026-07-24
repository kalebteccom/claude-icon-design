import hashlib
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "icon-design" / "skills" / "icon-design" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import render_suite  # noqa: E402
import validate_suite  # noqa: E402


class SuiteTests(unittest.TestCase):
    def write_source(self, root: Path, mark: str = None) -> Path:
        source = root / "source"
        shutil.copytree(ROOT / "tests" / "fixtures", source)
        if mark is not None:
            (source / "mark.svg").write_text(mark, encoding="utf-8")
        return source

    def test_render_validate_and_reproduce(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.write_source(root)
            output = root / "suite"
            archive = root / "test-mark-brand-suite.zip"

            files, written_archive = render_suite.render(source, output, archive)
            self.assertEqual(written_archive, archive)
            self.assertEqual(len(files), 21)
            validated = validate_suite.validate_suite(output, archive)
            self.assertEqual(len(validated), 21)

            first_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
            render_suite.render(output, output, archive)
            second_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual(first_hash, second_hash)

    def test_small_source_drives_small_favicons(self):
        small_mark = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">'
            '<path fill="currentColor" fill-rule="evenodd" '
            'd="M8 8 H88 V88 H8 Z M30 30 H66 V66 H30 Z"/></svg>'
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.write_source(root)
            stock_output = root / "stock"
            render_suite.render(source, stock_output, None)

            design = json.loads((source / "design.json").read_text())
            design["source_small_svg"] = "mark-small.svg"
            (source / "design.json").write_text(json.dumps(design))
            (source / "mark-small.svg").write_text(small_mark, encoding="utf-8")

            output = root / "suite"
            archive = root / "test-mark-brand-suite.zip"
            files, _ = render_suite.render(source, output, archive)
            self.assertEqual(len(files), 22)
            validated = validate_suite.validate_suite(output, archive)
            self.assertEqual(len(validated), 22)

            for size in (16, 32):
                self.assertNotEqual(
                    (output / f"favicon-{size}.png").read_bytes(),
                    (stock_output / f"favicon-{size}.png").read_bytes(),
                    f"favicon-{size} should render from the small master",
                )
            self.assertEqual(
                (output / "favicon-48.png").read_bytes(),
                (stock_output / "favicon-48.png").read_bytes(),
                "favicon-48 should keep rendering from the primary master",
            )

    def test_rejects_external_svg_reference(self):
        mark = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">
  <path fill="currentColor" d="M16 16h64v64H16z"/>
  <use href="https://example.com/mark.svg#part"/>
</svg>
"""
        with tempfile.TemporaryDirectory() as temporary:
            source = self.write_source(Path(temporary), mark)
            with self.assertRaisesRegex(ValueError, "references must stay inside"):
                render_suite.render(source, Path(temporary) / "suite", None)

    def test_rejects_hardcoded_master_color(self):
        mark = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">
  <rect x="16" y="16" width="64" height="64" fill="currentColor"/>
  <circle cx="48" cy="48" r="12" fill="#ff0000"/>
</svg>
"""
        with tempfile.TemporaryDirectory() as temporary:
            source = self.write_source(Path(temporary), mark)
            with self.assertRaisesRegex(ValueError, "Visible fill values"):
                render_suite.render(source, Path(temporary) / "suite", None)

    def test_rejects_default_black_geometry(self):
        mark = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">
  <rect x="16" y="16" width="64" height="64"/>
  <circle cx="48" cy="48" r="12" fill="currentColor"/>
</svg>
"""
        with tempfile.TemporaryDirectory() as temporary:
            source = self.write_source(Path(temporary), mark)
            with self.assertRaisesRegex(ValueError, "paint must resolve"):
                render_suite.render(source, Path(temporary) / "suite", None)

    def test_rejects_style_element(self):
        mark = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">
  <style>rect { fill: currentColor; }</style>
  <rect x="16" y="16" width="64" height="64"/>
</svg>
"""
        with tempfile.TemporaryDirectory() as temporary:
            source = self.write_source(Path(temporary), mark)
            with self.assertRaisesRegex(ValueError, "Disallowed SVG element: <style>"):
                render_suite.render(source, Path(temporary) / "suite", None)

    def test_rejects_stale_zip_member(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.write_source(root)
            output = root / "suite"
            archive = root / "test-mark-brand-suite.zip"
            render_suite.render(source, output, archive)
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zipped:
                for path in sorted(output.rglob("*")):
                    if path.is_file():
                        relative = path.relative_to(output).as_posix()
                        content = b"stale\n" if relative == "LICENSE" else path.read_bytes()
                        zipped.writestr(relative, content)
            with self.assertRaisesRegex(ValueError, "Zip member differs"):
                validate_suite.validate_suite(output, archive)


if __name__ == "__main__":
    unittest.main()
