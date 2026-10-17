# -*- coding: utf-8 -*-
"""End-to-End: echte TempApp + ECHTER Mausklick (SendInput) auf 'Aktualisieren'.
Testet Tk9-Events (CTkButton-Command), Scan-Pipeline, Tray-Start — sicher:
nur Scan (lesen), kein Loeschen.

Stand 2026-10-05:
- MOUSEINPUT.dwxtraInfo ist jetzt DWORD (vorher POINTER -> sizeof(INPUT_)=40
  statt 28 -> SendInput hat IMMER fehlschlagen, "Klicks" wurden nie gesendet).
- Der Start-Scan wird vor dem Test-Klick abgewartet, sonst ist "status_before"
  nicht belastbar (False Positive: der Start-Scan wuerde als Klick gezahlt).
- Vor dem Klick wird das Fenster lifted/focused, damit der SendInput-Klick
  nicht auf ein anderes, ueber der App liegendes Fenster trifft.

2. Review (2026-10-05):
- SendInput bekommt MOUSEEVENTF_ABSOLUTE (0x8000): ohne das Flag sind
  dx/dy RELATIVE Pixel-Verschiebungen vom aktuellen Cursor — der Klick
  landete bei cursor+(x,y), nicht bei (x,y). Jetzt: absolute Koordinaten
  auf den 0..65535-Bereich des VIRTUELLEN Screens (Multi-Monitor, negative
  Offsets via SM_X/YVIRTUALSCREEN) normiert.
- Klick-Erkennung ueber status_head ("Liest …") + _busy statt der
  Status-ZEILE: der 1-s-Status-Ticker schreibt "vor X Sekunden" jede
  Sekunde neu -> st != status_before wurde OHNE Klick wahr (False Positive).
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
# VIRTUELLER Screen (Multi-Monitor; kann negative Offsets haben)
VX0 = user32.GetSystemMetrics(76)   # SM_XVIRTUALSCREEN
VY0 = user32.GetSystemMetrics(77)   # SM_YVIRTUALSCREEN
VW  = user32.GetSystemMetrics(78)   # SM_CXVIRTUALSCREEN
VH  = user32.GetSystemMetrics(79)   # SM_CYVIRTUALSCREEN
print("Virtual Screen:", VX0, VY0, VW, VH)

class POINT(ctypes.Structure):
    _fields_ = [("x", wt.LONG), ("y", wt.LONG)]
# ACHTUNG (2026-10-06, SendInput-87-Fix): In den echten Windows-Headern ist
# MOUSEINPUT.dwExtraInfo ein ULONG_PTR (8 Byte auf x64) — NICHT DWORD!
# (Die vorige "DWORD-Fix"-Runde war falsch: das gepackte 28/32-Byte-Layout
# wird mit ERROR_INVALID_PARAMETER (87) abgelehnt.) Korrektes Layout x64:
# MOUSEINPUT=32 (28 + Padding), Union=32 (alle drei Mitglieder; KEYBDINPUT
# mit ULONG_PTR zwingt Alignment 8), INPUT=4 (type) + 4 (Padding) + 32 = 40.
# SendInput validiert cbSize gegen genau dieses sizeof(INPUT).
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
MOUSEEVENTF_MOVE, MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0001, 0x0002, 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000

# L8-Fix: Gesamtwatchdog (vorher KEINE -> unbegrenzter Hang moeglich) +
# Exit-Codes auf allen Fehlpfaden (vorher nur print -> Exit 0)
_done = {"flag": False}
def _watchdog():
    # 240 s: Deckt auch den haertbaren Klick-Pfad ab (3 Versuche x bis 8 s
    # Einschluss-Wartezeit) — vorher 120 s, das wurde mit den Retries knapp.
    time.sleep(240)
    if not _done["flag"]:
        print("WATCHDOG: Test haengt (>240 s) — Exit 3")
        os._exit(3)
threading.Thread(target=_watchdog, daemon=True).start()

fails = []
def record(name, cond):
    fails.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name)

def _abs(x, y):
    # Absolute Screen-Koordinate -> 0..65535 (SendInput-Norm) auf den
    # virtuellen Screen normiert und geclampt.
    dx = int((x - VX0) * 65535 / (VW - 1))
    dy = int((y - VY0) * 65535 / (VH - 1))
    return max(0, min(65535, dx)), max(0, min(65535, dy))

def real_click(x, y):
    def ev(flags):
        ax, ay = _abs(x, y)
        i = INPUT_(type=0, u=INPUT_._U(mi=MOUSEINPUT(dx=ax, dy=ay,
                                            mouseData=0,
                                            dwFlags=flags | MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                                            time=0, dwExtraInfo=0)))
        sent = user32.SendInput(1, ctypes.byref(i), ctypes.sizeof(INPUT_))
        if sent != 1:
            print(f"  WARNUNG: SendInput fehlgeschlagen (ret={sent}, GetLastError={ctypes.GetLastError()})")
    ev(0)  # move
    time.sleep(0.15)
    ev(MOUSEEVENTF_LEFTDOWN)
    time.sleep(0.08)
    ev(MOUSEEVENTF_LEFTUP)

app = tr.TempApp()
app.update_idletasks(); app.update()
time.sleep(0.3)
app.update()

# Start-Scan (aus dem Konstruktor) abwarten — erst DANN ist "status_before"
# ein belastbarer Ausgangszustand fuer die Klick-Erkennung
t0 = time.time()
while app._busy and time.time() - t0 < 60:
    app.update()
    time.sleep(0.1)
time.sleep(0.5)
app.update()
app.lift()
app.focus_force()

scan_btn = app.scan_button
scan_btn.update_idletasks()
sx = scan_btn.winfo_rootx() + scan_btn.winfo_width() // 2
sy = scan_btn.winfo_rooty() + scan_btn.winfo_height() // 2
print(f"Klicke auf 'Aktualisieren' bei ({sx},{sy})")

# Klick-Erkennung: status_head + _busy. NICHT die Status-ZEILE: der 1-s
# Ticker schreibt sie im ready-Modus jede Sekunde neu ("vor X Sekunden")
# -> text-change waere OHNE Klick ein garantierter False-Positive.
head_before = app.status_head.cget("text")

# Robustheit (2026-10-17): app.lift()/focus_force() bringen ein Fenster aus
# einem Hintergrund-Prozess heraus NICHT zwingend nach vorn (Foreground-Lock).
# Liegt ein fremdes Fenster ueber dem Button, trifft der physische Klick ins
# Leere (gemessen: "KEIN EINSCHLAG"). daher: Fenster pro Versuch per
# BringWindowToTop/HWND_TOP nach vorn (wirkt ohne Foreground-Rechte) und der
# Zielpunkt wird per WindowFromPoint verifiziert, bevor geklickt wird.
def _bring_ensure(x, y):
    root = user32.GetAncestor(app.winfo_id(), 2)   # GA_ROOT
    user32.BringWindowToTop(root)
    user32.SetWindowPos(root, 0, 0, 0, 0, 0, 0x1 | 0x2 | 0x10)  # TOP|NOSIZE|NOMOVE|NOACTIVATE
    time.sleep(0.3)
    app.update()
    pt = POINT(x, y)
    return user32.GetAncestor(user32.WindowFromPoint(pt), 2) == root

clicked = False
for _attempt in (1, 2, 3):
    if not _bring_ensure(sx, sy):
        print(f"  Hinweis: Zielpunkt ({sx},{sy}) liegt (noch) nicht auf "
              f"unserem Fenster — Retry nach BringWindowToTop")
    real_click(sx, sy)
    t0 = time.time()
    while time.time() - t0 < 8:
        app.update()
        head = app.status_head.cget("text")
        if head != head_before or app._busy:
            clicked = True
            print(f"EINSCHLAG: head='{head}' (vorher '{head_before}') | busy =", app._busy)
            break
        time.sleep(0.1)
    if clicked:
        break
    time.sleep(0.2)
if not clicked:
    print("KEIN EINSCHLAG nach 3 Versuchen (Button-Event nicht verarbeitet?)")
record("SendInput-Klick erzeugt Einschlag", clicked)

# auf Scan-Fertig warten (max 30 s)
t0 = time.time()
while app._busy and time.time() - t0 < 30:
    app.update()
    time.sleep(0.1)
print("Scan fertig. busy =", app._busy)
record("Start-Scan laeuft zu Ende (busy=False)", not app._busy)

# L4-cross-check: Gesamt muss der Summe der EINDEUTIGEN sicheren Ordner
# entsprechen (Duplikat zaehlt nur einmal; unsichere Karten zaehlen nicht).
# WICHTIG: Tween (560 ms) via Tk-after() PUMPEN lassen — blosses Schlafen
# ohne update() friert den Zwischenstand ein (after-Callbacks laufen nie).
t0 = time.time()
while time.time() - t0 < 1.5:
    app.update()
    time.sleep(0.05)
uniq_paths = {}
for c in app.cards:
    if c["safe"]:
        uniq_paths[os.path.realpath(c["path"]) if c["path"] else ("idx", c["idx"])] = c["bytes"] or 0
total_expected = sum(uniq_paths.values())
exp = tr.format_bytes(total_expected)
got = app.total_num.cget("text")
print(f"Total cross-check: angezeigt '{got}' erwartet '{exp}' "
      f"(unique Summe {total_expected} B, {len(uniq_paths)} Ordner)")
record("Gesamt = Summe eindeutiger sicherer Ordner", got == exp)
print("Status:", app.status_msg.cget("text"))
print("Cards:")
for c in app.cards:
    print("  ", c["title"], "->", c["num"].cget("text"), "|", c["count"].cget("text"))
print("Total:", app.total_num.cget("text"), "| Note:", app.total_note.cget("text"))
print("Tray aktiv:", app._tray_active, "| Tray ready:", app._tray_ready)

# Minimieren-Test: echtes Unmap-Event via iconify
app.update()
unmap_hits = []
app.bind("<Unmap>", lambda e: unmap_hits.append(1))
app.iconify()
t0 = time.time()
while time.time() - t0 < 2:
    app.update()
    time.sleep(0.05)
print("Unmap-Ereignisse nach iconify:", len(unmap_hits), "| state:", app.state())
record("Unmap-Event nach iconify", len(unmap_hits) >= 1)
# Tray-Zustand nach Minimieren (App withdraw() bei tray aktiv)
print("withdrawen?", app.state() == "withdrawn")

# Fenster Rueckholen (wie 'Fenster oeffnen')
app._show_window()
t0 = time.time()
while time.time() - t0 < 1.5:
    app.update()
    time.sleep(0.05)
print("state nach _show_window:", app.state())

app._do_quit()
print("QUIT OK")
_done["flag"] = True
nfails = sum(1 for _n, ok in fails if not ok)
print(f"ERGBNIS: {len(fails) - nfails}/{len(fails)} PASS, {nfails} FAIL")
sys.exit(1 if nfails else 0)
