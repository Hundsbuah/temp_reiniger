# -*- coding: utf-8 -*-
"""E2E sicherer Tray-Flow-Test: Fenster im Tray (withdrawn) -> Tray-Menu 'Alle leeren'
-> Bestaetigung-Dialog -> NEIN klicken (SendInput). Es wird NICHTS geloescht.

Stand 2026-10-05:
- MOUSEINPUT.dwExtraInfo ist jetzt DWORD (vorher POINTER -> sizeof(INPUT_)=40
  statt 28 -> SendInput hat IMMER fehlschlagen; der "Nein"-Klick wurde nie
  wirklich gesendet).
- EnumWindows/EnumChildWindows bekommen jetzt die PYTHON-Callback (cb(enum_cb)),
  nicht cb(0) = ctypes-Callback an Adresse 0 (NULL-Funktionspunktier -> AV).
- Dialogtitel-Match ist versionsunabhaengig (startswith "Temp-Reiniger").

2. Review (2026-10-05):
- SendInput: MOUSEEVENTF_ABSOLUTE + 0..65535-Normierung auf den VIRTUELLEN
  Screen (ohne das Flag waeren dx/dy relative Verschiebungen vom Cursor).
- Watchdog: askyesno blockiert den Main-Thread — fehlgeschlagener
  SendInput-Klick waere ein Ewigs-Hang im Modal. Nach 45 s ohne Abschluss:
  os._exit(3).
"""
import os, sys, time, ctypes, ctypes.wintypes as wt, threading
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location("tr", os.path.join(HERE, "temp_reiniger.py"))
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)

user32 = ctypes.windll.user32
# VIRTUELLER Screen (Multi-Monitor, kann negative Offsets haben)
VX0 = user32.GetSystemMetrics(76); VY0 = user32.GetSystemMetrics(77)
VW  = user32.GetSystemMetrics(78); VH  = user32.GetSystemMetrics(79)
WM = 0x0003; GWL_STYLE = -16; WS_DISABLED = 0x8000000

# ACHTUNG (2026-10-06, SendInput-87-Fix): MOUSEINPUT.dwExtraInfo ist
# ULONG_PTR (8 Byte auf x64), NICHT DWORD — gepackte 28/32-Byte-Layouts
# werden mit ERROR_INVALID_PARAMETER (87) abgelehnt. Korrektes x64-Layout:
# MOUSEINPUT=32, Union=32 (alle drei Mitglieder), INPUT=40. cbSize muss
# genau sizeof(INPUT) sein.
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wt.LONG), ("dy", wt.LONG), ("mouseData", wt.DWORD),
                ("dwFlags", wt.DWORD), ("time", wt.DWORD),
                ("dwExtraInfo", ctypes.c_size_t)]   # ULONG_PTR (x-Bit-treu)
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.c_size_t)]
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMessage", wt.DWORD), ("wParamL", wt.WORD), ("wParamH", wt.WORD)]
class INPUT_(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]
    _fields_ = [("type", wt.DWORD), ("u", _U)]
assert ctypes.sizeof(INPUT_) == 40, f"INPUT_-Layout kaputt: {ctypes.sizeof(INPUT_)} statt 40 (x64)"
MOUSEEVENTF_ABSOLUTE = 0x8000

_done = {"flag": False}
def _watchdog():
    # L8-Fix: NUR die Phase NACH dem Start-Scan abdecken. Vorher lief der
    # Watchdog ab Importzeitpunkt und kuehnte gueltige Laeufe weg, deren
    # Scan allein bis zu 60 s dauerte.
    time.sleep(45)
    if not _done["flag"]:
        print("WATCHDOG: Test haengt (Dialog vermutlich noch offen) — Exit 3")
        os._exit(3)

fails = []
def record(name, cond):
    fails.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name)

def click(x, y):
    def ev(flags):
        dx = max(0, min(65535, int((x - VX0) * 65535 / (VW - 1))))
        dy = max(0, min(65535, int((y - VY0) * 65535 / (VH - 1))))
        i = INPUT_(type=0, u=INPUT_._U(mi=MOUSEINPUT(dx=dx, dy=dy,
                                            mouseData=0,
                                            dwFlags=flags | 0x0001 | MOUSEEVENTF_ABSOLUTE,
                                            time=0, dwExtraInfo=0)))
        sent = user32.SendInput(1, ctypes.byref(i), ctypes.sizeof(INPUT_))
        if sent != 1:
            print(f"  WARNUNG: SendInput fehlgeschlagen (ret={sent}, GetLastError={ctypes.GetLastError()})")
    ev(0); time.sleep(0.12); ev(0x0002); time.sleep(0.08); ev(0x0004)

app = tr.TempApp()
app.update_idletasks(); app.update(); time.sleep(0.3); app.update()
# Start-Scan abwarten, damit "bytes vor Test" belastbar ist
t0 = time.time()
while app._busy and time.time() - t0 < 60:
    app.update()
    time.sleep(0.1)
time.sleep(0.3); app.update()
threading.Thread(target=_watchdog, daemon=True).start()   # hier: nach dem Scan-Warten
before = {c["idx"]: c["bytes"] for c in app.cards}
print("Bytes vor Test:", before)

# L9: Busy-Drop aus dem Tray muss FEEDBACK geben (nicht stumm verwerfen).
# _tray_action ist der ECHTE Tray-Thread-Einstiegspunkt (nur der physische
# Win32-Menü-Klick fehlt). 'card' waehrend busy -> Status-Meldung, kein Delete.
app._status_mode = "scanning"   # Ticker darf die Meldung nicht ueberschreiben
app._busy = True
app._tray_action("card", 0)
t0 = time.time()
fb = False
while time.time() - t0 < 3:
    app.update()
    if "Etwas läuft gerade" in app.status_msg.cget("text"):
        fb = True
        break
    time.sleep(0.05)
app._busy = False
app._status_mode = "ready"
record("tray busy-drop gibt Feedback (nicht stumm)", fb)

# L8: reales Menü bauen (Wiring-Check; pystray ohne Win32-Klick)
try:
    menu = app._build_menu()
    record("tray menü baut", menu is not None)
except Exception as e:
    record("tray menü baut", False)
    print("  menü-Fehler:", e)

# Fenster in den Tray (wie minimiert)
app.withdraw()
app.update(); time.sleep(0.3)

results = {}
def click_nein():
    time.sleep(3.0)   # Dialog warten
    ENUM = user32.EnumWindows
    cb = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    tops = []
    def enum_cb(h, _):
        if user32.IsWindowVisible(h):
            buf = ctypes.create_unicode_buffer(256)
            user32.GetWindowTextW(h, buf, 256)
            # Hauptfenster ausschliessen (versionsunabhaengig)
            if buf.value and not buf.value.startswith("Temp-Reiniger"):
                tops.append((h, buf.value))
        return True
    ENUM(cb(enum_cb), 0)
    dialog = None
    for h, t in tops:
        if "Temp-Ordner" in t or "leeren" in t:
            dialog = h
    results["tops"] = tops
    if dialog is None:
        results["dialog"] = "NICHT GEFUNDEN"
        return
    results["dialog"] = tops[[i for i, (h, t) in enumerate(tops) if h == dialog][0]][1]
    ENUMC = user32.EnumChildWindows
    btns = []
    def child_cb(h, _):
        buf = ctypes.create_unicode_buffer(64)
        user32.GetWindowTextW(h, buf, 64)
        if buf.value:
            btns.append((h, buf.value))
        return True
    ENUMC(dialog, cb(child_cb), 0)
    results["buttons"] = btns
    # Windows-Dialog-Buttons tragen den Accelerator-Praefix "&" (&Nein) —
    # das muss raus, sonst matcht exakter Text-Vergleich nie (2026-10-06).
    nein = next((h for h, t in btns
                 if t.replace("&", "").strip().lower() == "nein"), None)
    if nein is None:
        results["click"] = "NEIN-Button nicht gefunden"
        return
    # Robustheit (2026-10-17): Aus einem Hintergrund-Prozess ohne
    # Nutzer-Fokus oeffnet der Dialog ggf. HINTER anderen Fenstern im
    # Z-Order (Probe: fremdes Fenster oben -> Blind-Klick ins Leere,
    # Ewigs-Hang im Modal). SetForegroundWindow waere durch den
    # Foreground-Lock blockiert; BringWindowToTop + HWND_TOP reicht —
    # der Klick landet auf dem obersten Fenster an den Button-Pixeln.
    # ZUSAEZTLICH: Klick-Wirkung wird veriFIZIERT (Dialog wirklich zu?)
    # statt blind "gekl" = Erfolg anzunehmen; ein Retry holt Nachlaeufer.
    def _to_front():
        user32.BringWindowToTop(dialog)
        user32.SetWindowPos(dialog, 0, 0, 0, 0, 0,
                             0x1 | 0x2 | 0x10)   # NOSIZE|NOMOVE|NOACTIVATE
        time.sleep(0.3)
    for attempt in (1, 2):
        _to_front()
        r = wt.RECT()
        user32.GetWindowRect(nein, ctypes.byref(r))
        click((r.left + r.right) / 2, (r.top + r.bottom) / 2)
        t0 = time.time()
        while time.time() - t0 < 4.0:
            if not user32.IsWindow(dialog) or not user32.IsWindowVisible(dialog):
                results["click"] = "Nein geklickt (Dialog geschlossen)"
                return
            time.sleep(0.1)
    results["click"] = "KLICK WIRKUNGSLOS — Dialog noch offen"

t = threading.Thread(target=click_nein, daemon=True)
t.start()

# Tray-Aktion ausloesen — ECHTER Tray-Einstiegspunkt _tray_action('all', None)
# (L8-Fix: vorher direkter Queue-Put, der die reale Tray-Wiring umging)
app._tray_action("all", None)

t0 = time.time()
dialog_seen = False
while time.time() - t0 < 15:
    app.update()
    if results.get("click"):
        break
    time.sleep(0.05)
time.sleep(1.0)
for _ in range(20):
    app.update(); time.sleep(0.05)
print("TOPS:", results.get("tops"))
print("Dialog:", results.get("dialog"))
print("Buttons:", results.get("buttons"))
print("Click:", results.get("click"))
print("busy nachher:", app._busy, "| status:", app.status_msg.cget("text"))
record("Bestätigungs-Dialog gefunden", results.get("dialog") != "NICHT GEFUNDEN")
record("'Nein'-Button gefunden und Dialog geschlossen",
       results.get("click") == "Nein geklickt (Dialog geschlossen)")
after = {c["idx"]: c["bytes"] for c in app.cards}
print("Bytes nachher:", after)
nichts_geloest = (before == after) or all(v is None for v in before.values())
print("NICHTS GEOESCHT (bytes unveraendert):", nichts_geloest)
record("nichts gelöscht (Nein-Flow)", nichts_geloest)
_done["flag"] = True   # Watchdog entlassen (sonst waere er der Ewigs-Hang-Schutz, der zu spaet loest)
app._do_quit()
print("QUIT OK")
nfails = sum(1 for _n, ok in fails if not ok)
print(f"ERGBNIS: {len(fails) - nfails}/{len(fails)} PASS, {nfails} FAIL")
sys.exit(1 if nfails else 0)
