import hashlib
import json
import subprocess
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
    def write_svg(self, path: Path, inset: int = 14) -> None:
        path.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            f'<rect x="{inset}" y="{inset}" '
            f'width="{64 - inset * 2}" height="{64 - inset * 2}" '
            'rx="8" fill="currentColor"/></svg>\n',
            encoding="utf-8",
        )

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
            self.write_svg(root / filename, inset)
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

    def write_v2_refinement(
        self,
        root: Path,
        *,
        round_number: int = 1,
        start: int = 1,
        count: int = 4,
        parent_ids: tuple[str, ...] = ("D1-07",),
    ) -> Path:
        references = []
        for index, parent_id in enumerate(parent_ids, start=1):
            filename = f"{parent_id}.svg"
            self.write_svg(root / filename, 10 + index * 2)
            references.append(
                {
                    "id": parent_id,
                    "title": f"Parent {index}",
                    "file": filename,
                    "role": "parent",
                    "note": "Keep unchanged and selectable.",
                }
            )
        concepts = []
        for offset in range(count):
            concept_id = f"R{round_number}-{start + offset:02d}"
            filename = f"{concept_id}.svg"
            self.write_svg(root / filename, 13 + offset % 5)
            concepts.append(
                {
                    "id": concept_id,
                    "title": f"Move {offset + 1}",
                    "file": filename,
                    "parent": parent_ids[offset % len(parent_ids)],
                    "territory": "Proportion",
                    "move": "Changes one deliberate dimension.",
                    "watch": "Keep the counter open at 16 px.",
                    "risk": "May lose the parent's compact silhouette.",
                }
            )
        manifest = {
            "schema": "kalebtec.icon-round.v2",
            "project": "V2 Sheet Test",
            "wordmark": "V2 Sheet",
            "stage": "refinement",
            "round": round_number,
            "mode": "shortlist" if len(parent_ids) > 1 else "controlled",
            "count": count,
            "subtitle": "A controlled comparison against visible parents.",
            "references": references,
            "retired": [],
            "review": {"selection_max": 3},
            "concepts": concepts,
        }
        path = root / "concepts.json"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return path

    def write_v2_discovery(self, root: Path, count: int = 4) -> Path:
        concepts = []
        for offset in range(count):
            concept_id = f"D1-{offset + 1:02d}"
            filename = f"{concept_id}.svg"
            self.write_svg(root / filename, 12 + offset)
            concepts.append(
                {
                    "id": concept_id,
                    "title": f"Direction {offset + 1}",
                    "file": filename,
                    "territory": "Visible structure" if offset < 2 else "Clear signal",
                    "move": "Uses a distinct silhouette and construction.",
                    "watch": "Keep the counter open at native sizes.",
                }
            )
        manifest = {
            "schema": "kalebtec.icon-round.v2",
            "project": "V2 Discovery Test",
            "wordmark": "Discovery",
            "stage": "discovery",
            "round": 1,
            "mode": "territory",
            "count": count,
            "references": [],
            "retired": [],
            "review": {"selection_max": 4},
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
            html_output = output.with_suffix(".html")
            self.assertTrue(html_output.is_file())
            html_source = html_output.read_text(encoding="utf-8")
            self.assertIn("data:image/svg+xml;base64,", html_source)
            self.assertIn("Copy refinement request", html_source)
            self.assertNotRegex(html_source, r"<(?:script|link)[^>]+(?:src|href)=")
            with Image.open(output) as image:
                self.assertEqual(image.width, render_concept_sheet.PAGE_WIDTH)
                self.assertGreater(image.height, 1200)
                self.assertEqual(image.mode, "RGB")

    def test_renders_refinement_sheet(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.write_round(root, stage="refinement", count=8)
            output = root / "refinement-r1.png"
            self.assertEqual(
                render_concept_sheet.render(manifest, output), output.resolve()
            )
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

    def test_v2_renders_multi_parent_shortlist(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.write_v2_refinement(
                root, parent_ids=("D1-07", "D1-12"), count=4
            )
            output = root / "refinement-r1.png"
            render_concept_sheet.render(manifest, output)
            source = output.with_suffix(".html").read_text(encoding="utf-8")
            self.assertIn("From D1-07 · Parent 1", source)
            self.assertIn("From D1-12 · Parent 2", source)
            self.assertIn("References and benchmarks", source)
            self.assertIn("Copy final choice", source)
            self.assertIn("const max = 3;", source)
            self.assertIn("<small>Watch</small>", source)
            self.assertIn("<small>Risk</small>", source)

    def test_v2_discovery_groups_the_same_round_in_html(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.write_v2_discovery(root)
            output = root / "discovery-d1.png"
            render_concept_sheet.render(manifest, output)
            source = output.with_suffix(".html").read_text(encoding="utf-8")
            self.assertIn("Visible structure", source)
            self.assertIn("Clear signal", source)
            self.assertIn("Copy refinement request", source)
            self.assertIn("Copy discovery continuation", source)

    def test_v2_accepts_fresh_ids_after_retired_round(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_v2_refinement(
                root, round_number=4, start=13, count=3
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["retired"] = [f"R4-{number:02d}" for number in range(1, 13)]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            output = root / "refinement-r4.png"
            render_concept_sheet.render(manifest_path, output)
            source = output.with_suffix(".html").read_text(encoding="utf-8")
            self.assertIn("R4-13", source)
            self.assertIn("Retired: R4-01", source)

    def test_v2_rejects_unattributed_rating(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_v2_refinement(root, count=2)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["references"][0]["rating"] = {"value": 8.5, "out_of": 10}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "rating.attributed_to is required"):
                render_concept_sheet.render(manifest_path, root / "sheet.png")

    def test_v2_rejects_rating_on_a_new_concept(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_v2_refinement(root, count=2)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["concepts"][0]["rating"] = {
                "value": 8,
                "out_of": 10,
                "attributed_to": "Reviewer",
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "rating is not allowed"):
                render_concept_sheet.render(manifest_path, root / "sheet.png")

    def test_v2_rejects_parent_missing_from_reference_bar(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_v2_refinement(root, count=2)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["concepts"][0]["parent"] = "D1-12"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must appear in references"):
                render_concept_sheet.render(manifest_path, root / "sheet.png")

    def test_v2_rejects_control_as_candidate_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_v2_refinement(
                root, count=2, parent_ids=("D1-07", "D1-12")
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["references"][1]["role"] = "control"
            manifest["concepts"][0]["parent"] = "D1-12"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must use reference role 'parent'"):
                render_concept_sheet.render(manifest_path, root / "sheet.png")

    def test_v2_rejects_reference_file_from_another_id(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_v2_refinement(root, count=2)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.write_svg(root / "D1-12.svg")
            manifest["references"][0]["file"] = "D1-12.svg"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                ValueError, "file name must begin with 'D1-07'"
            ):
                render_concept_sheet.render(manifest_path, root / "sheet.png")

    def test_v2_requires_prior_ids_to_be_retired(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_v2_refinement(root, start=3, count=2)
            with self.assertRaisesRegex(ValueError, "list prior IDs in retired"):
                render_concept_sheet.render(manifest_path, root / "sheet.png")

    def test_v2_rejects_retired_id_reuse(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = self.write_v2_refinement(root, count=2)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["retired"] = ["R1-01"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "retired IDs must not appear"):
                render_concept_sheet.render(manifest_path, root / "sheet.png")

    def test_renderer_help_works_before_dependencies_are_installed(self):
        result = subprocess.run(
            [sys.executable, "-S", str(SCRIPTS / "render_concept_sheet.py"), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("matching PNG and HTML", result.stdout)

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
        self.assertIn("standalone HTML", source)
        self.assertIn("render_suite.py", source)
        self.assertIn("validate_suite.py", source)
        self.assertIn("Stop after the sheet", source)


if __name__ == "__main__":
    unittest.main()
