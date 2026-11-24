#!/usr/bin/env python3
"""Jajko korowe w Studio (Paweł 24.11): model z swiat/postacie/jajko_korowe.py zbudowany narzędziem Karola
swiat/postacie/roblox_postac.py (części Roblox z klipami z Blendera) we WŁASNYM kontenerze
Workspace/JajkoKorowePodglad (atrybut Wygenerowane), na wolnym bruku placu obok kotów ras. W Play skrypt
PokazAnimacji gra po kolei spoczynek, napięcie i pęknięcie. Słup światła (kość Promien) Roblox pokazuje zawsze
(skali z klipu nie przenosi) — w grze zapala go klient przy wykluciu.

Użycie: python -B tools/studio/jajko_korowe_studio.py [--usun]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "swiat", "postacie"))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import roblox_postac as R  # noqa: E402

R.KONTENER = "JajkoKorowePodglad"
R.PRZESUNIECIE = (0.0, 0.0)
R.ROZMIESZCZENIE = {"jajko_korowe": {"poz": (983.0, -652.0), "patrz": (983.0, -666.0), "nazwa": "Jajko korowe"}}

if __name__ == "__main__":
    reszta = [a for a in sys.argv[1:] if a == "--usun"]
    sys.argv = [sys.argv[0], "--tylko", "jajko_korowe", "--wyj", os.path.join(ROOT, "build", "jajko_korowe")] + reszta
    R.main()
