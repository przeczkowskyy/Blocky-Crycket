#!/usr/bin/env python3
"""Wysyla plik(i) na jednorazowe upload URL-e zwrocone przez Figma MCP `upload_assets`.

  python tools/figma_upload.py assets/processed/IconArena.png "https://mcp.figma.com/mcp/upload/.../submit?..."
  python tools/figma_upload.py A.png URL_A B.png URL_B ...      # kilka par naraz

URL-e sa jednorazowe i wygasaja po ~10 min – jesli wygasly, popros Figma MCP o nowe.
"""
from __future__ import annotations

import json
import mimetypes
import sys
from pathlib import Path

import requests


def upload(path: Path, url: str) -> dict:
    ctype = mimetypes.guess_type(path.name)[0] or "image/png"
    with path.open("rb") as fh:
        r = requests.post(url, files={"file": (path.name, fh, ctype)}, timeout=180)
    try:
        body = r.json()
    except ValueError:
        body = {"raw": r.text[:500]}
    return {"file": str(path), "status": r.status_code, **body}


def main(argv: list[str]) -> int:
    if len(argv) < 2 or len(argv) % 2:
        print(__doc__)
        return 2
    results, ok = [], True
    for i in range(0, len(argv), 2):
        p = Path(argv[i])
        if not p.exists():
            results.append({"file": str(p), "error": "brak pliku"}); ok = False; continue
        res = upload(p, argv[i + 1])
        ok = ok and res.get("status") == 200 and res.get("success", True)
        results.append(res)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
