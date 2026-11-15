#!/usr/bin/env python3
"""Zamienia plik Rojo *.model.json na kod Luau, który buduje te same instancje w Studio (przez MCP).

Po co: gdy Rojo nie jest podłączony do miejsca z chmury (Team Create), GUI z plików trzeba wstawić
skryptem. Obsługiwane typy wartości (jak w generatorach tools/*_build_gui.py):
  {"UDim2": [[s,o],[s,o]]} · {"UDim": [s,o]} · {"Font": {...}} · {"ColorSequence": {...}}
  lista 3 liczb -> Color3 · lista 2 liczb -> Vector2 · string -> tekst albo nazwa enuma (Roblox sam zamienia)
  liczby, bool. Atrybuty -> SetAttribute.

Użycie jako moduł:  build_luau(model_dict, var="root") -> str  (kod tworzy drzewo i zostawia je w zmiennej `var`)
"""
import json


def _lua_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def _value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return _lua_str(v)
    if isinstance(v, list):
        if len(v) == 3:
            return f"Color3.new({v[0]}, {v[1]}, {v[2]})"
        if len(v) == 2:
            return f"Vector2.new({v[0]}, {v[1]})"
    if isinstance(v, dict):
        if "UDim2" in v:
            (xs, xo), (ys, yo) = v["UDim2"]
            return f"UDim2.new({xs}, {xo}, {ys}, {yo})"
        if "UDim" in v:
            s, o = v["UDim"]
            return f"UDim.new({s}, {o})"
        if "Font" in v:
            f = v["Font"]
            return f"Font.new({_lua_str(f['family'])}, Enum.FontWeight.{f.get('weight', 'Regular')}, Enum.FontStyle.{f.get('style', 'Normal')})"
        if "ColorSequence" in v:
            kps = ", ".join(f"ColorSequenceKeypoint.new({k['time']}, Color3.new({k['color'][0]}, {k['color'][1]}, {k['color'][2]}))"
                            for k in v["ColorSequence"]["keypoints"])
            return f"ColorSequence.new({{{kps}}})"
    raise ValueError(f"nieobsługiwana wartość: {v!r}")


def build_luau(model: dict, var: str = "root", name: str | None = None) -> str:
    lines, counter = [], [0]

    def emit(n: dict, parent: str | None, fallback_name: str | None) -> str:
        counter[0] += 1
        v = f"I[{counter[0]}]"  # tabela zamiast zmiennych lokalnych (limit 200 locali w Luau)
        lines.append(f"{v} = Instance.new({_lua_str(n['ClassName'])})")
        nm = n.get("Name", fallback_name)
        if nm:
            lines.append(f"{v}.Name = {_lua_str(nm)}")
        for k, val in n.get("Properties", {}).items():
            lines.append(f"{v}.{k} = {_value(val)}")
        for k, val in n.get("Attributes", {}).items():
            lines.append(f"{v}:SetAttribute({_lua_str(k)}, {_value(val)})")
        for c in n.get("Children", []):
            emit(c, v, None)
        if parent:
            lines.append(f"{v}.Parent = {parent}")
        return v

    lines.append("local I = {}")
    top = emit(model, None, name)
    lines.append(f"local {var} = {top}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    m = json.loads(open(sys.argv[1], encoding="utf-8").read())
    print(build_luau(m, name=sys.argv[2] if len(sys.argv) > 2 else None))
