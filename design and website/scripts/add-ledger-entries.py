#!/usr/bin/env python3 -I
"""Adds rights-ledger entries (release-manifest.json `rights_ledger` and asset-rights.json `assets`) for binary files under assets/public/assets.
Usage (repository root): python3 "design and website/scripts/add-ledger-entries.py" <glob under 'design and website/'> --source "<how the file was made>" --evidence "<path>" [--condition "<text>"]...
Rights state is always `owned` (made by the owner's tools); conditions must carry limits such as fictional people or unverified likeness. Run refresh-manifest.py afterwards."""
import argparse, hashlib, json, pathlib, sys
P = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser(); ap.add_argument("glob"); ap.add_argument("--source", required=True); ap.add_argument("--evidence", action="append", required=True); ap.add_argument("--condition", action="append", default=[])
a = ap.parse_args(); files = sorted(p for p in P.glob(a.glob) if p.is_file())
if not files: sys.exit("no files match")
def entry(f):
    b = f.read_bytes(); rel = f.relative_to(P).as_posix()
    return {"path": rel, "repository_path": "design and website/" + rel, "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b), "source": a.source, "rights_state": "owned", "evidence": a.evidence, "source_hash_match": False, "conditions": a.condition or ["Proposed; owner acceptance pending."]}
for fn, key in (("asset-rights.json", "assets"), ("release-manifest.json", "rights_ledger")):
    q = P / fn; d = json.loads(q.read_text()); rows = {r["path"]: r for r in d[key]}
    for f in files: rows[f.relative_to(P).as_posix()] = entry(f)
    d[key] = list(rows.values()); q.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print(len(files), "entries added or updated")
