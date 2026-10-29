import json
import tempfile
import unittest
from pathlib import Path

from research.collector.writing_graph import GRAPH_RELATIVE_PATH, WRITING_SOURCES, build_writing_graph


class WritingGraphTests(unittest.TestCase):
    def make_sources(self, root: Path) -> None:
        for source in WRITING_SOURCES:
            path = root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            if source.endswith(".json"):
                path.write_text('{"audience":"builders"}\n', encoding="utf-8")
            else:
                path.write_text("# Method\n\n## Evidence\n\nSee [category](CATEGORY-GUIDE.md).\n", encoding="utf-8")

    def test_graph_tracks_source_hashes_links_and_allowlisted_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_sources(root)
            report = build_writing_graph(root)
            graph = json.loads((root / GRAPH_RELATIVE_PATH).read_text(encoding="utf-8"))

            self.assertTrue(report["valid"])
            self.assertEqual(set(WRITING_SOURCES), set(report["source_hashes"]))
            self.assertTrue(all(node["source_file"] in WRITING_SOURCES for node in graph["nodes"]))
            self.assertTrue(all(edge["source_file"] in WRITING_SOURCES for edge in graph["edges"]))
            reference_edges = [edge for edge in graph["edges"] if edge["relation"] == "references"]
            # Every synthetic Markdown source contains one explicit local link.
            self.assertEqual(4, len(reference_edges))
            self.assertTrue(any(edge["relation"] == "contains" for edge in graph["edges"]))
            self.assertFalse(graph["metadata"]["semantic_inference"])

    def test_rebuild_changes_hash_and_removes_deleted_source_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_sources(root)
            first = build_writing_graph(root)
            changed = root / WRITING_SOURCES[0]
            changed.write_text(changed.read_text(encoding="utf-8") + "\n## Added\n", encoding="utf-8")
            (root / WRITING_SOURCES[1]).unlink()

            second = build_writing_graph(root)
            graph = json.loads((root / GRAPH_RELATIVE_PATH).read_text(encoding="utf-8"))
            self.assertNotEqual(first["source_hashes"][WRITING_SOURCES[0]], second["source_hashes"][WRITING_SOURCES[0]])
            self.assertIn(WRITING_SOURCES[1], second["missing_sources"])
            self.assertNotIn(WRITING_SOURCES[1], second["source_hashes"])
            self.assertFalse(any(node["source_file"] == WRITING_SOURCES[1] for node in graph["nodes"]))
            self.assertFalse(any(edge["target"] == "file_docs_category_guide_md" for edge in graph["edges"]))


if __name__ == "__main__":
    unittest.main()
