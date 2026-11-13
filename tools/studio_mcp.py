#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Klient MCP do Roblox Studio (sama biblioteka standardowa) — używany przez panel i przez Claude'a z terminala.

Roblox Studio ma wbudowany serwer MCP; mostek to `%LOCALAPPDATA%\\Roblox\\mcp.bat` (Windows) uruchamiany przez stdio.
Ten plik rozmawia z nim JSON-RPC bez żadnych zależności, więc działa też wtedy, gdy sesja Claude Code nie ma
podłączonego serwera `Roblox_Studio`.

Użycie (CLI):
    python tools/studio_mcp.py tools                       # lista narzędzi (nazwa + opis)
    python tools/studio_mcp.py tools --json                # pełne schematy
    python tools/studio_mcp.py studios                     # otwarte okna Studio (studio_id)
    python tools/studio_mcp.py call <narzedzie> --args '{"klucz": "wartosc"}'
    python tools/studio_mcp.py call execute_luau --args-file plik.json
    python tools/studio_mcp.py luau plik.luau              # skrót: execute_luau z kodem z pliku (auto studio_id)
    python tools/studio_mcp.py call screen_capture --out zrzut.png

Zmienne: STUDIO_MCP_CMD (inne polecenie mostka), STUDIO_MCP_TIMEOUT (sekundy, domyślnie 120).
"""
import argparse
import base64
import json
import os
import queue
import subprocess
import sys
import threading

PROTOCOL = "2025-06-18"
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _bridge_cmd():
    env = os.environ.get("STUDIO_MCP_CMD")
    if env:
        return env
    if os.name == "nt":
        bat = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Roblox", "mcp.bat")
        if not os.path.isfile(bat):
            raise StudioError("Nie ma mostka MCP: %s. Włącz w Studio: Assistant → … → Manage MCP Servers → "
                              "Enable Studio as MCP server." % bat)
        return 'cmd.exe /c "%s"' % bat
    # macOS: Studio instaluje mostek w ~/Library/Application Support/Roblox/mcp.sh (wg dokumentacji)
    sh = os.path.expanduser("~/Library/Application Support/Roblox/mcp.sh")
    if os.path.isfile(sh):
        return '"%s"' % sh
    raise StudioError("Nie znaleziono mostka MCP Roblox Studio (ustaw STUDIO_MCP_CMD).")


class StudioError(RuntimeError):
    pass


class StudioMCP:
    """Jedna sesja z mostkiem. Użycie: `with StudioMCP() as s: s.call("list_roblox_studios")`."""

    def __init__(self, timeout=None):
        self.timeout = float(timeout or os.environ.get("STUDIO_MCP_TIMEOUT") or 120)
        self._id = 0
        self._proc = None
        self._q = queue.Queue()
        self._lock = threading.Lock()
        self.server_info = None

    # --- życie procesu
    def start(self):
        cmd = _bridge_cmd()
        self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      shell=True, creationflags=CREATE_NO_WINDOW)
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self._drain_err, daemon=True).start()
        res = self._request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {},
                                           "clientInfo": {"name": "blocky-crycket-panel", "version": "0.1"}})
        self.server_info = res
        self._notify("notifications/initialized")
        return self

    def close(self):
        p = self._proc
        self._proc = None
        if p:
            try:
                p.stdin.close()
            except Exception:
                pass
            try:
                p.wait(timeout=3)
            except Exception:
                try:
                    p.terminate()
                except Exception:
                    pass

    def alive(self):
        return bool(self._proc and self._proc.poll() is None)

    def __enter__(self):
        return self.start()

    def __exit__(self, *a):
        self.close()

    # --- transport
    def _reader(self):
        p = self._proc
        try:
            for line in p.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    self._q.put(json.loads(line.decode("utf-8", "replace")))
                except ValueError:
                    continue
        finally:
            self._q.put(None)

    def _drain_err(self):
        p = self._proc
        try:
            for _ in p.stderr:
                pass
        except Exception:
            pass

    def _send(self, obj):
        data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
        try:
            self._proc.stdin.write(data)
            self._proc.stdin.flush()
        except Exception as e:
            raise StudioError("Mostek MCP nie przyjmuje danych (%r). Czy Roblox Studio jest uruchomione?" % (e,))

    def _notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)

    def _request(self, method, params=None, timeout=None):
        with self._lock:
            self._id += 1
            rid = self._id
            msg = {"jsonrpc": "2.0", "id": rid, "method": method}
            if params is not None:
                msg["params"] = params
            self._send(msg)
            while True:
                try:
                    m = self._q.get(timeout=timeout or self.timeout)
                except queue.Empty:
                    raise StudioError("Brak odpowiedzi z Roblox Studio na „%s” w %.0f s." % (method, timeout or self.timeout))
                if m is None:
                    raise StudioError("Mostek MCP zakończył pracę. Czy Roblox Studio jest uruchomione i ma włączony serwer MCP?")
                if m.get("id") != rid:
                    continue                                # powiadomienia i odpowiedzi na inne żądania
                if "error" in m:
                    raise StudioError("MCP %s: %s" % (method, json.dumps(m["error"], ensure_ascii=False)))
                return m.get("result")

    # --- API
    def tools(self):
        out, cursor = [], None
        while True:
            res = self._request("tools/list", {"cursor": cursor} if cursor else {})
            out += res.get("tools", [])
            cursor = res.get("nextCursor")
            if not cursor:
                return out

    def call(self, name, arguments=None, timeout=None):
        """Zwraca dict: {"text": str, "images": [bytes], "is_error": bool, "raw": wynik MCP}."""
        res = self._request("tools/call", {"name": name, "arguments": arguments or {}}, timeout=timeout)
        texts, images = [], []
        for c in (res or {}).get("content", []):
            if c.get("type") == "text":
                texts.append(c.get("text", ""))
            elif c.get("type") == "image":
                try:
                    images.append(base64.b64decode(c.get("data", "")))
                except Exception:
                    pass
        return {"text": "\n".join(texts), "images": images, "is_error": bool((res or {}).get("isError")), "raw": res}

    def studios(self, wait=6.0):
        """Otwarte okna Studio. Mostek potrzebuje chwili, żeby je zobaczyć — przy pustej liście ponawiamy do `wait` s."""
        import time
        t0 = time.time()
        while True:
            r = self.call("list_roblox_studios")
            try:
                d = json.loads(r["text"])
            except ValueError:
                return [{"raw": r["text"]}]
            lst = d if isinstance(d, list) else (d.get("studios") or d.get("instances") or [])
            if lst or time.time() - t0 >= wait:
                return lst
            time.sleep(0.5)


def first_studio_id(session):
    """studio_id pierwszego otwartego okna (albo None)."""
    for s in session.studios():
        if isinstance(s, dict):
            for k in ("studio_id", "studioId", "id"):
                if s.get(k):
                    return s[k]
    return None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Klient MCP Roblox Studio")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("tools")
    p.add_argument("--json", action="store_true")
    sub.add_parser("studios")
    p = sub.add_parser("call")
    p.add_argument("name")
    p.add_argument("--args", default=None, help="JSON z argumentami")
    p.add_argument("--args-file", default=None, help="plik JSON z argumentami")
    p.add_argument("--out", default=None, help="zapisz obraz z odpowiedzi do pliku")
    p.add_argument("--raw", action="store_true", help="wypisz surową odpowiedź MCP")
    p = sub.add_parser("luau")
    p.add_argument("file")
    p.add_argument("--studio", default=None)
    p.add_argument("--dm", default="Edit", choices=["Edit", "Client", "Server"], help="datamodel_type (domyślnie Edit)")
    p.add_argument("--extra", default=None, help="JSON z dodatkowymi argumentami execute_luau")
    a = ap.parse_args()
    try:
        with StudioMCP() as s:
            if a.cmd == "tools":
                tools = s.tools()
                if a.json:
                    print(json.dumps(tools, ensure_ascii=False, indent=1))
                else:
                    for t in tools:
                        print("%-28s %s" % (t["name"], (t.get("description") or "").split("\n")[0][:150]))
            elif a.cmd == "studios":
                print(json.dumps(s.studios(), ensure_ascii=False, indent=1))
            elif a.cmd == "call":
                args = {}
                if a.args_file:
                    with open(a.args_file, encoding="utf-8-sig") as f:
                        args = json.load(f)
                elif a.args:
                    args = json.loads(a.args)
                r = s.call(a.name, args)
                if a.raw:
                    raw = dict(r["raw"] or {})
                    for c in raw.get("content", []):
                        if c.get("type") == "image":
                            c["data"] = "<%d znaków base64>" % len(c.get("data", ""))
                    print(json.dumps(raw, ensure_ascii=False, indent=1))
                else:
                    print(r["text"])
                if r["images"]:
                    if a.out:
                        with open(a.out, "wb") as f:
                            f.write(r["images"][0])
                        print("[obraz zapisany: %s, %d bajtów]" % (a.out, len(r["images"][0])))
                    else:
                        print("[odpowiedź zawiera %d obraz(y) — użyj --out plik.png]" % len(r["images"]))
                if r["is_error"]:
                    sys.exit(2)
            elif a.cmd == "luau":
                with open(a.file, encoding="utf-8-sig") as f:
                    code = f.read()
                sid = a.studio or first_studio_id(s)
                args = {"code": code, "datamodel_type": a.dm}
                if sid:
                    args["studio_id"] = sid
                if a.extra:
                    args.update(json.loads(a.extra))
                r = s.call("execute_luau", args)
                print(r["text"])
                if r["is_error"]:
                    sys.exit(2)
    except StudioError as e:
        print("BŁĄD: %s" % e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
