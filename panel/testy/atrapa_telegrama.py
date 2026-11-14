# -*- coding: utf-8 -*-
"""Atrapa API Telegrama dla testów: mały lokalny serwer HTTP (127.0.0.1, losowy port), który zapisuje otrzymane
żądania i podaje zaplanowane aktualizacje. Nigdy nie łączy się z prawdziwym Telegramem.

    a = AtrapaTelegrama(TOKEN); a.start()
    bot = telegram.Bot(api=a.adres, synchronicznie=True)      # albo zmienne trybu testowego dla serwera panelu
    a.dodaj_aktualizacje({"message": {...}})                   # update_id nadaje atrapa
    a.zadania("sendMessage")                                   # [pola żądania, …]
    a.awaria["sendMessage"] = "500" | "400" | "siec"           # błąd serwera, zły czat albo zerwane połączenie
    a.stop()
"""
import http.server
import json
import threading
import time


class AtrapaTelegrama:
    def __init__(self, token):
        self.token = token
        self.lista = []                                        # [(metoda, pola, ścieżka)]
        self.aktualizacje = []
        self.awaria = {}
        self.nastepny_update = 1
        self.nastepna_wiadomosc = 500
        self.cond = threading.Condition()
        atrapa = self

        class Obsluga(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *a):
                return

            def do_POST(self):
                dl = int(self.headers.get("Content-Length") or 0)
                cialo = self.rfile.read(dl) if dl else b""
                try:
                    pola = json.loads(cialo.decode("utf-8") or "{}")
                except ValueError:
                    pola = {}
                czesci = self.path.strip("/").split("/")
                if len(czesci) != 2 or czesci[0] != "bot" + atrapa.token:
                    return self._json(401, {"ok": False, "error_code": 401, "description": "Unauthorized"})
                metoda = czesci[1]
                with atrapa.cond:
                    atrapa.lista.append((metoda, pola, self.path))
                    atrapa.cond.notify_all()
                    awaria = atrapa.awaria.get(metoda)
                if awaria == "siec":
                    self.close_connection = True
                    try:
                        self.connection.shutdown(2)
                    except OSError:
                        pass
                    return
                if awaria == "400":
                    return self._json(400, {"ok": False, "error_code": 400, "description": "Bad Request: chat not found"})
                if awaria:
                    return self._json(500, {"ok": False, "error_code": 500, "description": "Internal Server Error"})
                if metoda == "getUpdates":
                    return self._json(200, {"ok": True, "result": atrapa._daj_aktualizacje(pola)})
                if metoda == "sendMessage":
                    with atrapa.cond:
                        atrapa.nastepna_wiadomosc += 1
                        mid = atrapa.nastepna_wiadomosc
                    return self._json(200, {"ok": True, "result": {"message_id": mid, "chat": {"id": pola.get("chat_id")},
                                                                   "text": pola.get("text")}})
                return self._json(200, {"ok": True, "result": True})

            def _json(self, status, obj):
                b = json.dumps(obj).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)

        class Serwer(http.server.ThreadingHTTPServer):
            def handle_error(self, request, client_address):
                return                                         # klient (panel) zerwał połączenie, np. przy zamykaniu

        self.serwer = Serwer(("127.0.0.1", 0), Obsluga)
        self.serwer.daemon_threads = True
        self.adres = "http://127.0.0.1:%d" % self.serwer.server_address[1]
        self._watek = None

    def start(self):
        self._watek = threading.Thread(target=self.serwer.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True)
        self._watek.start()
        return self

    def stop(self):
        self.serwer.shutdown()
        self.serwer.server_close()

    def _daj_aktualizacje(self, pola):
        """Jak Telegram: aktualizacje o numerze >= offset; czeka najwyżej 1 s (zamiast `timeout`), żeby testy szły szybko."""
        offset = pola.get("offset") or 0
        koniec = time.time() + min(1.0, float(pola.get("timeout") or 0))
        with self.cond:
            while True:
                gotowe = [u for u in self.aktualizacje if u["update_id"] >= offset]
                if gotowe or time.time() >= koniec:
                    return gotowe
                self.cond.wait(max(0.01, koniec - time.time()))

    def dodaj_aktualizacje(self, u):
        with self.cond:
            u = dict(u, update_id=self.nastepny_update)
            self.nastepny_update += 1
            self.aktualizacje.append(u)
            self.cond.notify_all()
            return u["update_id"]

    def zadania(self, metoda=None):
        with self.cond:
            return [p for m, p, _ in self.lista if metoda is None or m == metoda]

    def sciezki(self):
        with self.cond:
            return [s for _, _, s in self.lista]

    def wyczysc(self):
        with self.cond:
            self.lista.clear()

    def czekaj_na(self, metoda, ile=1, czas=10.0, warunek=None):
        """Czeka, aż przyjdzie co najmniej `ile` żądań danej metody (spełniających `warunek`)."""
        koniec = time.time() + czas
        with self.cond:
            while True:
                lista = [p for m, p, _ in self.lista if m == metoda and (warunek is None or warunek(p))]
                if len(lista) >= ile or time.time() >= koniec:
                    return lista
                self.cond.wait(max(0.01, koniec - time.time()))


# --------------------------------------------------------------------------- aktualizacje jak z Telegrama
def wiadomosc(czat, od, tekst, prywatna=False, odpowiedz_na=None, nr=1):
    m = {"message_id": nr, "from": {"id": od, "is_bot": False, "first_name": "X"},
         "chat": {"id": czat, "type": "private" if prywatna else "supergroup"}, "date": 0, "text": tekst}
    if odpowiedz_na:
        m["reply_to_message"] = {"message_id": odpowiedz_na}
    return {"message": m}


def klikniecie(czat, od, dane, wiadomosc_nr=77, tekst="Pytanie", prywatna=False):
    return {"callback_query": {"id": "cb%d" % wiadomosc_nr, "from": {"id": od, "is_bot": False, "first_name": "X"},
                               "data": dane, "message": {"message_id": wiadomosc_nr, "text": tekst,
                                                         "chat": {"id": czat, "type": "private" if prywatna else "supergroup"}}}}
