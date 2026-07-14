import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "icon-design" / "skills" / "icon-design"
SCRIPTS = SKILL / "scripts"
LLMS = ROOT / "public" / "llms.txt"
sys.path.insert(0, str(SCRIPTS))

import launch_brief_builder  # noqa: E402
import render_concept_sheet  # noqa: E402


class WorkflowTests(unittest.TestCase):
    def write_round(
        self,
        root: Path,
        *,
        stage: str = "discovery",
        round_number: int = 1,
        count: int = 20,
    ) -> Path:
        prefix = "D" if stage == "discovery" else "R"
        concepts = []
        for index in range(1, count + 1):
            concept_id = f"{prefix}{round_number}-{index:02d}"
            filename = f"{concept_id}.svg"
            inset = 10 + index % 8
            (root / filename).write_text(
                "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 64 64\">"
                f"<rect x=\"{inset}\" y=\"{inset}\" "
                f"width=\"{64 - inset * 2}\" height=\"{64 - inset * 2}\" "
                "rx=\"8\" fill=\"currentColor\"/></svg>\n",
                encoding="utf-8",
            )
            concepts.append(
                {
                    "id": concept_id,
                    "title": f"Direction {index}",
                    "file": filename,
                    "territory": f"Territory {index}",
                    "note": "A distinct construction move for comparison.",
                }
            )
        manifest = {
            "project": "Sheet Test",
            "stage": stage,
            "round": round_number,
            "count": count,
            "selected_parent": None if stage == "discovery" else "D1-07",
            "concepts": concepts,
        }
        path = root / "concepts.json"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return path

    def test_renders_deterministic_discovery_sheet(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.write_round(root)
            output = root / "discovery-d1.png"
            render_concept_sheet.render(manifest, output)
            first_hash = hashlib.sha256(output.read_bytes()).hexdigest()
            render_concept_sheet.render(manifest, output)
            second_hash = hashlib.sha256(output.read_bytes()).hexdigest()
            self.assertEqual(first_hash, second_hash)
            with Image.open(output) as image:
                self.assertEqual(image.width, render_concept_sheet.PAGE_WIDTH)
                self.assertGreater(image.height, 1200)
                self.assertEqual(image.mode, "RGB")

    def test_renders_refinement_sheet(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.write_round(root, stage="refinement", count=8)
            output = root / "refinement-r1.png"
            self.assertEqual(render_concept_sheet.render(manifest, output), output.resolve())
            self.assertTrue(output.is_file())

    def test_rejects_out_of_sequence_ids(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_round(root, count=2)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["concepts"][1]["id"] = "D1-09"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "D1-02"):
                render_concept_sheet.render(manifest_path, root / "sheet.png")

    def test_rejects_mismatched_filename(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_round(root, count=2)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["concepts"][0]["file"] = "D1-02.svg"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "D1-01.*\.svg"):
                render_concept_sheet.render(manifest_path, root / "sheet.png")

    def test_rejects_invalid_refinement_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_round(root, stage="refinement", count=8)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["selected_parent"] = "chosen one"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "valid discovery or refinement ID"):
                render_concept_sheet.render(manifest_path, root / "sheet.png")

    def test_brief_builder_is_packaged(self):
        path = launch_brief_builder.builder_path()
        source = path.read_text(encoding="utf-8")
        self.assertIn("kalebtec.icon-brief.v1", source)
        self.assertIn("__ICON_BRIEF_BUILDER__", source)
        self.assertIn("Discovery prompt", source)
        self.assertIn("aria-valuetext", source)
        self.assertIn("64 lower/higher landmarks", source)
        self.assertIn("Guided", source)
        self.assertIn("Custom", source)
        self.assertIn("radiogroup", source)
        self.assertIn("Customize delivery", source)
        self.assertIn("Made with love", source)
        self.assertRegex(source, r"conceptCount:\s*20")
        self.assertNotRegex(source, r"<script[^>]+src=")
        self.assertNotRegex(source, r"<link[^>]+stylesheet")
        self.assertTrue(path.as_uri().startswith("file://"))

    def test_agent_guide_covers_the_complete_workflow(self):
        source = LLMS.read_text(encoding="utf-8")
        self.assertTrue(source.startswith("# Kalebtec Icon Design"))
        self.assertIn("$icon-design", source)
        self.assertIn("/icon-design:icon-design", source)
        self.assertIn("D1-01", source)
        self.assertIn("R1-01", source)
        self.assertIn("render_concept_sheet.py", source)
        self.assertIn("render_suite.py", source)
        self.assertIn("validate_suite.py", source)
        self.assertIn("Stop after the sheet", source)


if __name__ == "__main__":
    unittest.main()
