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
SW = user32.GetSystemMetrics(0); SH = user32.GetSystemMetrics(1)
WM = 0x0003; GWL_STYLE = -16; WS_DISABLED = 0x8000000

class MOUSEINPUT(ctypes.Structure):
    # dwExtraInfo ist DWORD (4 Byte), NICHT ein Pointer — sonst stimmt
    # sizeof(INPUT_) nicht und SendInput lehnt cbSize ab.
    _fields_ = [("dx", wt.LONG), ("dy", wt.LONG), ("mouseData", wt.DWORD),
                ("dwFlags", wt.DWORD), ("time", wt.DWORD), ("dwExtraInfo", wt.DWORD)]
class INPUT_(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _fields_ = [("type", wt.DWORD), ("u", _U)]
assert ctypes.sizeof(INPUT_) == 28, f"INPUT_-Layout kaputt: {ctypes.sizeof(INPUT_)} statt 28"

def click(x, y):
    def ev(flags):
        i = INPUT_(type=0, u=INPUT_._U(mi=MOUSEINPUT(dx=int(x * (SW - 1) / SW), dy=int(y * (SH - 1) / SH),
                                            mouseData=0, dwFlags=flags | 0x0001, time=0, dwExtraInfo=0)))
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
before = {c["idx"]: c["bytes"] for c in app.cards}
print("Bytes vor Test:", before)

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
    nein = next((h for h, t in btns if t.strip().lower() == "nein"), None)
    if nein is None:
        results["click"] = "NEIN-Button nicht gefunden"
        return
    r = wt.RECT()
    user32.GetWindowRect(nein, ctypes.byref(r))
    click((r.left + r.right) / 2, (r.top + r.bottom) / 2)
    results["click"] = "Nein geklickt"

t = threading.Thread(target=click_nein, daemon=True)
t.start()

# Tray-Aktion ausloesen (genau wie _tray_action('all'))
app._ui_queue.put(app._confirm_tray_all)

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
after = {c["idx"]: c["bytes"] for c in app.cards}
print("Bytes nachher:", after)
print("NICHTS GEOESCHT (bytes unveraendert):", before == after or all(v is None for v in before.values()))
app._do_quit()
print("QUIT OK")
