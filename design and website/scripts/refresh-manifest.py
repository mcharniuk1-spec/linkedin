#!/usr/bin/env python3 -I
"""Refreshes design and website/release-manifest.json (`files` list with sizes and SHA-256) and the hashes of the rights-ledger entries in
release-manifest.json and asset-rights.json after files were added or edited. It never invents a rights entry: add the entry first, then run this.
Usage (from the repository root): python3 "design and website/scripts/refresh-manifest.py" """
import hashlib, json, sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent
EXCLUDED = {"node_modules", "dist", "storybook-static", "__pycache__", ".cache", ".vite", ".hyperframes", "inbox"}
man = json.loads((P / "release-manifest.json").read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
payload = sorted(p.relative_to(P).as_posix() for p in P.rglob("*")
                 if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(P).parts) and p.name not in {"release-manifest.json", ".DS_Store"})
man["files"] = [{"path": r, "bytes": (P / r).stat().st_size, "sha256": sha(P / r)} for r in payload]
missing = []
for x in man["rights_ledger"]:
    f = P / x["path"]
    if not f.exists(): missing.append(x["path"]); continue
    x["sha256"] = sha(f); x["bytes"] = f.stat().st_size
(P / "release-manifest.json").write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n")
ar = P / "asset-rights.json"
if ar.exists():
    d = json.loads(ar.read_text())
    for x in d.get("assets", []):
        f = P / x["path"]
        if f.exists(): x["sha256"] = sha(f); x["bytes"] = f.stat().st_size
    ar.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({"files": len(man["files"]), "rights": len(man["rights_ledger"]), "ledger_paths_missing": missing}))
sys.exit(1 if missing else 0)
