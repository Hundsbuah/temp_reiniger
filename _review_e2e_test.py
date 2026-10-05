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
"""
import os, sys, time, ctypes, ctypes.wintypes as wt
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location("tr", os.path.join(HERE, "temp_reiniger.py"))
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)

user32 = ctypes.windll.user32
SM_CXSCREEN, SM_CYSCREEN = 0, 1
SW = user32.GetSystemMetrics(SM_CXSCREEN)
SH = user32.GetSystemMetrics(SM_CYSCREEN)
print("Screen:", SW, SH)

class POINT(ctypes.Structure):
    _fields_ = [("x", wt.LONG), ("y", wt.LONG)]
class MOUSEINPUT(ctypes.Structure):
    # ACHTUNG: dwExtraInfo ist DWORD (4 Byte), NICHT ein Pointer —
    # sonst ist sizeof(INPUT_) falsch und SendInput lehnt cbSize ab.
    _fields_ = [("dx", wt.LONG), ("dy", wt.LONG), ("mouseData", wt.DWORD),
                ("dwFlags", wt.DWORD), ("time", wt.DWORD), ("dwExtraInfo", wt.DWORD)]
class INPUT_(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _fields_ = [("type", wt.DWORD), ("u", _U)]
assert ctypes.sizeof(INPUT_) == 28, f"INPUT_-Layout kaputt: {ctypes.sizeof(INPUT_)} statt 28"
MOUSEEVENTF_MOVE, MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0001, 0x0002, 0x0004

def real_click(x, y):
    def ev(flags):
        i = INPUT_(type=0, u=INPUT_._U(mi=MOUSEINPUT(dx=int(x * (SW - 1) / SW), dy=int(y * (SH - 1) / SH),
                                            mouseData=0, dwFlags=flags | MOUSEEVENTF_MOVE,
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

status_before = app.status_msg.cget("text")
real_click(sx, sy)

t0 = time.time()
clicked = False
while time.time() - t0 < 8:
    app.update()
    st = app.status_msg.cget("text")
    if st != status_before or app._busy:
        clicked = True
        print("EINSCHLAG: Status =", st, "| busy =", app._busy)
        break
    time.sleep(0.1)
if not clicked:
    print("KEIN EINSCHLAG nach 8 s (Button-Event nicht verarbeitet?)")

# auf Scan-Fertig warten (max 30 s)
t0 = time.time()
while app._busy and time.time() - t0 < 30:
    app.update()
    time.sleep(0.1)
print("Scan fertig. busy =", app._busy)
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
