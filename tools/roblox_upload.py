#!/usr/bin/env python3
"""Upload obrazkow do Roblox przez Open Cloud Assets API.

  python tools/roblox_upload.py check                                   # test klucza / konfiguracji
  python tools/roblox_upload.py upload assets/processed/X.png --name X   # upload (wymaga akceptacji w manifescie!)
  python tools/roblox_upload.py status <operationId>                    # status operacji

BEZPIECZNIK: upload jest blokowany, jesli w assets/manifest.json asset <name> nie ma
`approved_by_user: true` ORAZ `approved_sha256` zgodnego z wysylanym plikiem.
Akceptacje ustawia sie dopiero po pokazaniu obrazka uzytkownikowi i jego "tak":
  python tools/manifest.py approve X
`--force` istnieje tylko do testow i wymaga wpisania nazwy assetu drugi raz (--confirm X).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

API = "https://apis.roblox.com/assets/v1"
ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "assets" / "manifest.json"


def env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        sys.exit(f"Brak zmiennej {name} w .env (patrz README_SETUP.md §2.2)")
    return v


def creator() -> dict:
    kind = env("ROBLOX_CREATOR_TYPE").lower()
    cid = env("ROBLOX_CREATOR_ID")
    if kind not in ("user", "group"):
        sys.exit("ROBLOX_CREATOR_TYPE musi byc 'user' albo 'group'")
    return {"userId": cid} if kind == "user" else {"groupId": cid}


def headers() -> dict:
    return {"x-api-key": env("ROBLOX_API_KEY")}


def sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def approval_problem(name: str, path: Path) -> str | None:
    """None = OK. Akceptacja musi dotyczyc DOKLADNIE tego pliku (sha256)."""
    if not MANIFEST.exists():
        return "brak assets/manifest.json"
    a = json.loads(MANIFEST.read_text(encoding="utf-8")).get("assets", {}).get(name)
    if not a:
        return f"brak wpisu '{name}' w manifescie"
    if a.get("approved_by_user") is not True:
        return f"'{name}' nie ma approved_by_user=true"
    if a.get("approved_sha256") != sha256(path):
        return "plik zmienil sie od momentu akceptacji (sha256 sie nie zgadza) – pokaz go ponownie i zaakceptuj"
    return None


def get_operation(op_id: str) -> dict:
    r = requests.get(f"{API}/operations/{op_id}", headers=headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def cmd_check(_: argparse.Namespace) -> int:
    creator(); headers()
    # nieistniejaca operacja: 404 = klucz dziala; 401/403 = problem z kluczem/uprawnieniami/IP
    r = requests.get(f"{API}/operations/00000000-0000-0000-0000-000000000000", headers=headers(), timeout=30)
    verdict = {401: "ZLY KLUCZ", 403: "BRAK UPRAWNIEN (Assets API Read/Write) albo IP spoza listy"}.get(
        r.status_code, "OK (klucz przyjety)" if r.status_code in (400, 404) else f"nieoczekiwany status {r.status_code}")
    print(json.dumps({"http": r.status_code, "verdict": verdict, "creator": creator()}, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("OK") else 1


def cmd_upload(a: argparse.Namespace) -> int:
    path = Path(a.file)
    if not path.exists():
        sys.exit(f"Brak pliku: {path}")
    problem = approval_problem(a.name, path)
    if problem and not (a.force and a.confirm == a.name):
        print(json.dumps({
            "error": "BRAK AKCEPTACJI",
            "message": f"{problem}. Pokaz finalny obrazek uzytkownikowi i poczekaj na 'tak' (SKILL.md krok 5b), "
                       f"potem: python tools/manifest.py approve {a.name}",
        }, ensure_ascii=False, indent=2))
        return 3
    ctype = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".bmp": "image/bmp", ".tga": "image/tga"}.get(
        path.suffix.lower())
    if not ctype:
        sys.exit("Obslugiwane: png, jpg, bmp, tga")
    req = {
        "assetType": "Decal",
        "displayName": a.name[:50],
        "description": a.description or f"Blocky&Crycket asset: {a.name}",
        "creationContext": {"creator": creator()},
    }
    with path.open("rb") as fh:
        r = requests.post(f"{API}/assets", headers=headers(),
                          data={"request": json.dumps(req)},
                          files={"fileContent": (path.name, fh, ctype)}, timeout=180)
    if r.status_code not in (200, 202):
        print(json.dumps({"error": r.status_code, "body": r.text[:800]}, ensure_ascii=False, indent=2))
        return 1
    op = r.json()
    op_id = (op.get("path") or "").split("/")[-1] or op.get("operationId")
    result = op
    deadline = time.time() + a.timeout
    while not result.get("done") and time.time() < deadline:
        time.sleep(2)
        result = get_operation(op_id)
    resp = result.get("response") or {}
    out = {
        "name": a.name,
        "operationId": op_id,
        "done": bool(result.get("done")),
        "decalId": resp.get("assetId"),
        "assetType": resp.get("assetType"),
        "moderationState": (resp.get("moderationResult") or {}).get("moderationState"),
        "next": "Uruchom tools/resolve_image_id.luau w Studio z DECAL_ID, zeby dostac imageId (SKILL.md krok 7).",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out["decalId"] else 1


def cmd_status(a: argparse.Namespace) -> int:
    print(json.dumps(get_operation(a.operation_id), ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    u = sub.add_parser("upload")
    u.add_argument("file")
    u.add_argument("--name", required=True)
    u.add_argument("--description", default="")
    u.add_argument("--timeout", type=int, default=90)
    u.add_argument("--force", action="store_true", help="tylko testy; wymaga --confirm <name>")
    u.add_argument("--confirm", default="")
    u.set_defaults(fn=cmd_upload)
    s = sub.add_parser("status")
    s.add_argument("operation_id")
    s.set_defaults(fn=cmd_status)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
