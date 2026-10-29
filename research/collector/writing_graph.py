"""Build a small, deterministic Graphify-compatible index of writing methods.

The graph is derived from a fixed documentation allowlist. It contains only
file, heading, explicit Markdown-link and containment relationships; it does
not infer semantic similarity or evaluate writing quality.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit


WRITING_SOURCES = (
    "docs/SERVICES-AND-WRITING.md",
    "docs/CATEGORY-GUIDE.md",
    "docs/SEARCH-AND-QUALIFICATION.md",
    "docs/APPROVED-POSITIONING.json",
    "docs/positioning-and-copy.md",
)
GRAPH_RELATIVE_PATH = "knowledge/writing/graph.json"
MANIFEST_VERSION = 1


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _node_id(path: str, kind: str, suffix: str = "") -> str:
    stem = re.sub(r"[^a-z0-9]+", "_", path.lower()).strip("_")
    if suffix:
        stem += "_" + re.sub(r"[^a-z0-9]+", "_", suffix.lower()).strip("_")
    return f"{kind}_{stem}"


def _heading_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-") or "section"


def _local_markdown_target(source: str, target: str) -> str | None:
    """Resolve only a local path target; ignore external and fragment-only URLs."""
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    decoded = unquote(parsed.path)
    resolved = PurePosixPath(source).parent.joinpath(decoded)
    parts: list[str] = []
    for part in resolved.parts:
        if part in ("", ".", "/"):
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
        else:
            parts.append(part)
    return PurePosixPath(*parts).as_posix()


def _extract(repo_root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    root = repo_root.resolve()
    source_hashes: dict[str, str] = {}
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    file_node_by_path: dict[str, str] = {}
    headings_by_file: dict[str, list[tuple[int, int, str]]] = {}
    pending_links: list[tuple[str, str, str, int]] = []

    for relative in WRITING_SOURCES:
        path = root / relative
        if not path.is_file():
            continue
        content = path.read_bytes()
        digest = _sha256(content)
        source_hashes[relative] = digest
        text = content.decode("utf-8")
        file_id = _node_id(relative, "file")
        file_node_by_path[relative] = file_id
        nodes.append({
            "id": file_id,
            "label": Path(relative).name,
            "file_type": "document",
            "source_file": relative,
            "source_location": None,
            "source_hash": digest,
        })

        per_file: list[tuple[int, int, str]] = []
        seen_slug: dict[str, int] = {}
        if relative.lower().endswith(".md"):
            for line_number, line in enumerate(text.splitlines(), start=1):
                match = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
                if not match:
                    continue
                level = len(match.group(1))
                title = match.group(2).strip()
                slug = _heading_slug(title)
                seen_slug[slug] = seen_slug.get(slug, 0) + 1
                heading_id = _node_id(relative, "heading", f"{slug}_{seen_slug[slug]}")
                nodes.append({
                    "id": heading_id,
                    "label": title,
                    "file_type": "document",
                    "source_file": relative,
                    "source_location": f"line {line_number}",
                    "source_hash": digest,
                })
                edges.append({
                    "source": file_id,
                    "target": heading_id,
                    "relation": "contains",
                    "confidence": "EXTRACTED",
                    "confidence_score": 1.0,
                    "source_file": relative,
                    "source_location": f"line {line_number}",
                    "weight": 1.0,
                })
                per_file.append((level, line_number, heading_id))
            headings_by_file[relative] = per_file

            for line_number, line in enumerate(text.splitlines(), start=1):
                for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", line):
                    target = _local_markdown_target(relative, match.group(1).split()[0].strip("<>"))
                    if target is not None:
                        pending_links.append((relative, target, line_number, 1))

    # Structural parent-child edges follow Markdown heading levels and order.
    for source, heading_rows in headings_by_file.items():
        stack: list[tuple[int, str, int]] = []
        for level, line_number, heading_id in heading_rows:
            while stack and stack[-1][0] >= level:
                stack.pop()
            if stack:
                parent_id = stack[-1][1]
                edges.append({
                    "source": parent_id,
                    "target": heading_id,
                    "relation": "contains",
                    "confidence": "EXTRACTED",
                    "confidence_score": 1.0,
                    "source_file": source,
                    "source_location": f"line {line_number}",
                    "weight": 1.0,
                })
            stack.append((level, heading_id, line_number))

    for source, target, line_number, _ in pending_links:
        if target in file_node_by_path:
            edges.append({
                "source": file_node_by_path[source],
                "target": file_node_by_path[target],
                "relation": "references",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": source,
                "source_location": f"line {line_number}",
                "weight": 1.0,
            })

    # Stable ordering makes diffs and repeated builds reproducible.
    nodes.sort(key=lambda row: row["id"])
    edges.sort(key=lambda row: (row["source"], row["relation"], row["target"], row["source_location"] or ""))
    graph = {
        "nodes": nodes,
        "edges": edges,
        "hyperedges": [],
        "input_tokens": 0,
        "output_tokens": 0,
        "metadata": {
            "generator": "research.collector.writing_graph",
            "schema_version": MANIFEST_VERSION,
            "source_hashes": source_hashes,
            "relations": ["contains", "references"],
            "semantic_inference": False,
        },
    }
    return graph, source_hashes


def build_writing_graph(repo_root: str | Path) -> dict[str, Any]:
    """Rebuild the small allowlisted graph and return its integrity report.

    Rebuilding the full bounded scope on each call handles additions, edits,
    deletions and renamed sources without stale nodes or edges.
    """
    root = Path(repo_root)
    graph, hashes = _extract(root)
    output = root / GRAPH_RELATIVE_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    output.write_text(serialized, encoding="utf-8")
    allowlisted = set(WRITING_SOURCES)
    node_ids = {node["id"] for node in graph["nodes"]}
    invalid_sources = sorted({
        node.get("source_file", "") for node in graph["nodes"]
        if node.get("source_file") not in allowlisted
    } | {
        edge.get("source_file", "") for edge in graph["edges"]
        if edge.get("source_file") not in allowlisted
    })
    dangling_edges = [
        edge for edge in graph["edges"]
        if edge["source"] not in node_ids or edge["target"] not in node_ids
    ]
    return {
        "graph_path": GRAPH_RELATIVE_PATH,
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "source_hashes": hashes,
        "missing_sources": sorted(allowlisted - set(hashes)),
        "invalid_source_paths": invalid_sources,
        "dangling_edges": len(dangling_edges),
        "valid": not invalid_sources and not dangling_edges,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_writing_graph(args.repo_root), indent=2, sort_keys=True))
