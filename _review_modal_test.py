# -*- coding: utf-8 -*-
"""Modal-/Poller-/Lifecycle-Tests (Review-Runde 2026-10-17).

Pinnt die Fixes der Review gegen echte Tk-Ausführung — OHNE physisches
Löschen echter Temp-Daten und OHNE SendInput (kein Fokus-Klau):
- M1: Tray "Alle leeren" — Busy-Flip WÄHREND des offenen Bestätigungs-
      dialogs -> explizites "Ja" darf nicht stumm verschwinden.
- M2: _poll_ui Re-Entry — ein laufendes Kommando (z. B. Modal) darf nicht
      unter sich selbst dräiniert werden; Reihen beweisen die Reihenfolge.
- T3: Per-Kommando-Netz des Pollers — ein poison-Kommando tötet ihn nicht.
- M3/T5: Tray-Degradation (Setup-Thread tot + unsichtbar) holt ein
      WITHDRAWN Fenster zurück und meldet den Hinweis.
- T8: Yes-Path ende-zu-ende gegen einen SCRATCH-Ordner als %TEMP%
      (Env-Override nur für diesen Test; echtes %TEMP% bleibt unangetastet).
"""
import os, sys, time, tempfile, shutil, threading, importlib.util
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("tr", os.path.join(HERE, "temp_reiniger.py"))
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)

_done = {"flag": False}
def _watchdog():
    time.sleep(90)
    if not _done["flag"]:
        print("WATCHDOG: Test hängt — Exit 3")
        os._exit(3)
threading.Thread(target=_watchdog, daemon=True).start()

fails = []
def record(name, cond, extra=""):
    fails.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + (" | " + extra if extra else ""))

def pump(app, seconds, until):
    """Tk-Eventloop ~seconds lang pumpen, bis until() True ist."""
    t0 = time.time()
    while time.time() - t0 < seconds:
        app.update()
        if until():
            return True
        time.sleep(0.02)
    app.update()
    return bool(until())

app = tr.TempApp(initial_scan=False)   # kein Start-Scan: keine Worker-Stoerung
app.update_idletasks(); app.update()

# --- T3: Per-Kommando-Netz des Pollers (poison darf ihn nicht toeten) ---
seen = []
def _boom():
    raise RuntimeError("poison (Test) — muss im ui_poll-Netz landen")
app._ui_queue.put(_boom)
app._ui_queue.put(lambda: seen.append("after"))
record("T3: Poller-Netz — poison-Kommando ueberlebt, draening geht weiter",
       pump(app, 3.0, lambda: "after" in seen))
app._ui_queue.put(lambda: seen.append("later"))
record("T3: Poller lebt danach noch (Poller-Kette intakt)",
       pump(app, 3.0, lambda: "later" in seen))

# --- M1: Busy-Flip waehrend Modal -> "Ja" mit Feedback, kein stummer Drop ---
calls = []
real_dfc = tr.delete_folder_contents
def _spy(p):
    calls.append(p)
    return (0, 0, 0, 0)
tr.delete_folder_contents = _spy
real_ask = tr.tk_messagebox.askyesno
_stub_n = {"n": 0}
def _stub_ask(*a, **k):
    _stub_n["n"] += 1
    if _stub_n["n"] == 1:
        # 1. Runde: simuliert den Auto-Rescan (+3 s), der WAEHREND des
        # offenen Dialogs busy setzt -> "Ja" muss Feedback bekommen.
        # 2. Runde: ohne Busy -> dasselbe Kommando MUSS durchgehen.
        app._busy = True
    return True
tr.tk_messagebox.askyesno = _stub_ask
app._confirm_tray_all()
app.update()
txt = app.status_msg.cget("text")
record("M1: 'Ja' bei Busy am Dialog-Ende -> Feedback (nicht still)",
       "Etwas läuft gerade" in txt, txt)
record("M1: bei Busy wurde NICHTS deletiert", not calls)
record("M1: busy-Zustand bleibt erhalten (laufender Worker)", app._busy)
# ohne Busy: dasselbe Kommando muss durchgehen (Einzig-Guard unveraendert)
app._busy = False
app._confirm_tray_all()
ok_start = pump(app, 5.0, lambda: bool(calls))
record("M1: 'Ja' ohne Busy -> Delete-Worker startet (Spy gerufen)", ok_start)
pump(app, 3.0, lambda: not app._busy)
app._cancel_rescan()                 # Auto-Rescan (3 s) nicht nachziehen lassen
tr.tk_messagebox.askyesno = real_ask
tr.delete_folder_contents = real_dfc

# --- M2: Poller-Re-Entry — dräint NICHT unter dem laufenden Kommando ---
drained = []
def _slow():
    # wie ein Modal: waehrend fn() laeuft, feuert der after()-Timer -> der
    # re-entrant aufgerufene Poller muss NO-OP sein (kein Draening, kein
    # extra Reschedule)
    app._ui_queue.put(lambda: drained.append("inner"))
    app._poll_ui()                    # Re-Entry -> darf nicht draenen
    drained.append("notyet")
app._ui_queue.put(_slow)
pump(app, 3.0, lambda: drained)
record("M2: Re-Entry-Poller dräint nicht unter dem Modal (Reihenfolge)",
       drained[:2] == ["notyet", "inner"], f"drained={drained}")

# --- M3/T5: Tray-Degradation: Fenster zurück + Hinweis ---
dead = threading.Thread(target=lambda: None)
dead.start(); dead.join()
class _StubIcon:
    _setup_thread = dead
    visible = False
app._tray_icon = _StubIcon()
app._tray_started = time.monotonic() - 10   # jenseits der 3-s-Grace
app._tray_active = True
app._tray_degraded_hint = False
app.withdraw(); app.update()
app._tray_health()
back = pump(app, 1.0, lambda: app.state() != "withdrawn")
record("M3: Degradation holt withdrawn-Fenster zurueck (nichtunerreichbar)",
       back, f"state={app.state()}")
record("M3/T5: Degradation -> tray_active=False + Status-Hinweis",
       (not app._tray_active)
       and "Tray-Icon nicht verfügbar" in app.status_msg.cget("text"),
       app.status_msg.cget("text"))
app._show_window(); app.update()

# --- T8: Yes-Path (arm -> ausloesen) gegen SCRATCH-Ordner als %TEMP% ---
scratch = tempfile.mkdtemp(prefix="tr_t8_")
t_temp = os.path.join(scratch, "a-temp")          # Suffix-Regel: endet auf temp
os.makedirs(os.path.join(t_temp, "sub"))
with open(os.path.join(t_temp, "sub", "f.bin"), "wb") as f:
    f.write(b"y" * 10)
real_temp_dir = os.environ.get("TEMP")
sent = os.path.join(real_temp_dir, "tr_t8_sentinel.txt")
with open(sent, "wb") as f:
    f.write(b"s")
saved = {k: os.environ.get(k) for k in ("TEMP", "TMP")}
os.environ["TEMP"] = os.environ["TMP"] = t_temp
app2 = None
ok8 = {"done": False}
try:
    app2 = tr.TempApp(initial_scan=True)          # baut Karten aus ueberlagertem %TEMP%
    scanned = pump(app2, 60,
                   lambda: (not app2._busy) and app2.cards[0]["bytes"] == 10)
    record("T8: scratch-%TEMP% eingelesen (bytes=10)", scanned,
           f"bytes={app2.cards[0]['bytes']}")
    app2._on_card_delete(0)                       # Klick 1: armieren
    record("T8: erster Klick armiert (Zwei-Stufen)", app2.cards[0]["armed"])
    app2._on_card_delete(0)                       # Klick 2: echtes Loeschen
    def _empty():
        # Latch: Inhalt weg UND _on_deleted hat die Completion gemeldet
        # (Status "entfernt") — der Auto-Rescan (+3 s) ueberschreibt sie spaeter.
        if (not ok8["done"]) and os.path.isdir(t_temp) \
                and os.listdir(t_temp) == [] \
                and "entfernt" in app2.status_msg.cget("text"):
            ok8["done"] = True
        return ok8["done"]
    finished = pump(app2, 30, _empty)
    record("T8: Yes-Path leert scratch-Inhalt, _on_deleted meldet 'entfernt'",
           finished, f"rest={os.listdir(t_temp)} status={app2.status_msg.cget('text')}")
    record("T8: Root-Ordner bleibt stehen", os.path.isdir(t_temp))
    record("T8: echtes %TEMP% unangetastet (Sentinel da)", os.path.exists(sent))
finally:
    if app2 is not None:
        app2._do_quit()
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    try:
        os.remove(sent)
    except OSError:
        pass
    shutil.rmtree(scratch, ignore_errors=True)

_done["flag"] = True
app._do_quit()
print("QUIT OK")
nfails = sum(1 for _n, ok in fails if not ok)
print(f"ERGBNIS: {len(fails) - nfails}/{len(fails)} PASS, {nfails} FAIL")
sys.exit(1 if nfails else 0)
