# -*- coding: utf-8 -*-
"""Review-Teste fuer temp_reiniger.py (lokale Funktionsverifikation).

Stand 2026-10-05: Erwartungen an Windows-Semantik wurden gegen das GEMESSENE
Verhalten auf Win11 (26200) korrigiert:
- Read-only-ATTRIBUT auf einem ORDNER blockiert das Loeschen von KINDERdateien
  NICHT (nur ACLs/Rechte tun das) -> der chmod-Trick greift nur bei
  Read-only-DATEIEN.
- os.path.realpath normalisiert auf Windows den Case auf die On-Disk-Schreibung
  -> die Deduplizierung der App ist case-sicher.

2. Review (2026-10-05): neu —
- Junction-Test (mklink /J, OHNE Admin/Dev-Mode): Regression gegen H1-Bug
  (os.path.islink() erkennt Junctions NICHT -> os.walk lief durch sie und
  delete loeschte die ZIEL-Inhalte). Jetzt: _is_reparse_point (0x400) pruenft.
- locked-File-Test: skipped-Pfad (Handle ohne FILE_SHARE_DELETE -> remove
  blockiert) — vorher wurde nur der skipped==0-Pfad getestet.
- PB-/TB-Randwerte von format_bytes.
"""
import os, sys, stat, time, tempfile, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("tr", os.path.join(HERE, "temp_reiniger.py"))
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)

BASE = tempfile.mkdtemp(prefix="tr_review_")
results = []

def check(name, cond, extra=""):
    results.append((name, bool(cond), extra))
    print(("PASS " if cond else "FAIL ") + name + (" | " + extra if extra else ""))

# --- 1. Baum aufbauen ---
root = os.path.join(BASE, "top")
sub = os.path.join(root, "sub")
deep = os.path.join(sub, "deep")
ro_dir = os.path.join(root, "ro_dir")
for d in (root, sub, deep, ro_dir):
    os.makedirs(d)
def wf(p, n):
    with open(p, "wb") as f:
        f.write(b"x" * n)
wf(os.path.join(sub, "a.txt"), 1000)
wf(os.path.join(deep, "b.txt"), 500)
wf(os.path.join(ro_dir, "locked.txt"), 100)
wf(os.path.join(root, "rofile.txt"), 100)
os.chmod(os.path.join(root, "rofile.txt"), stat.S_IREAD)   # read-only DATEI
os.chmod(ro_dir, stat.S_IREAD)                             # read-only ORDNER

# --- 2. scan ---
total, count = tr.scan_folder(root)
check("scan: total=1700", total == 1700, f"total={total}")
check("scan: count=4", count == 4, f"count={count}")
check("scan: nonexistent=(0,0)", tr.scan_folder(os.path.join(BASE, "nix")) == (0, 0))
check("scan: empty path=(0,0)", tr.scan_folder("") == (0, 0))

# --- 3. delete ---
freed, deleted, skipped = tr.delete_folder_contents(root)
check("delete: root bleibt", os.path.isdir(root))
check("delete: sub a.txt weg", not os.path.exists(os.path.join(sub, "a.txt")))
check("delete: deep b.txt weg", not os.path.exists(os.path.join(deep, "b.txt")))
check("delete: leerer sub weg", not os.path.exists(sub))
check("delete: leerer deep weg", not os.path.exists(deep))
check("delete: read-only DATEI weg (chmod-Trick)", not os.path.exists(os.path.join(root, "rofile.txt")))
# Read-only-ORDNER blockiert auf modernem Windows/NTFS das Loeschen von
# KINDERdateien NICHT -> locked.txt wird normal geloest, danach ist der Ordner
# leer und (via chmod-Retry) ebenfalls weg
check("delete: read-only Ordner: Datei trotzdem weg (NTFS-Semantik)",
      not os.path.exists(os.path.join(ro_dir, "locked.txt")))
check("delete: read-only Ordner weg (leer + chmod-Retry)", not os.path.isdir(ro_dir))
check("delete: freed=1700", freed == 1700, f"freed={freed}")
check("delete: deleted=4", deleted == 4, f"deleted={deleted}")
check("delete: skipped=0", skipped == 0, f"skipped={skipped}")

# --- 4. leerer read-only Ordner wird entfernt ---
ro2 = os.path.join(BASE, "ro2")
os.makedirs(os.path.join(ro2, "inner"))
os.chmod(os.path.join(ro2, "inner"), stat.S_IREAD)
f2, d2, s2 = tr.delete_folder_contents(ro2)
check("delete: leerer read-only Ordner entfernt", not os.path.exists(os.path.join(ro2, "inner")),
      f"freed={f2} deleted={d2} skipped={s2}")

# --- 5. delete: nicht vorhanden ---
check("delete: nonexistent=(0,0,0)", tr.delete_folder_contents(os.path.join(BASE, "nix")) == (0, 0, 0))

# --- 6. Formatierung ---
fb = tr.format_bytes
check("fmt: 0 B", fb(0) == "0 B", fb(0))
check("fmt: 999 B", fb(999) == "999 B", fb(999))
# Regressions-Tests für den PB-Boundary-Bug (1000..1023 durften nie "PB" sein)
check("fmt: 1000 B (Grenze)", fb(1000) == "1000 B", fb(1000))
check("fmt: 1023 B (Grenze)", fb(1023) == "1023 B", fb(1023))
check("fmt: 1024 = 1 KB", fb(1024) == "1 KB", fb(1024))
check("fmt: 1536 = 1,5 KB", fb(1536) == "1,5 KB", fb(1536))
check("fmt: 1 MB", fb(1024*1024) == "1 MB", fb(1024*1024))
check("fmt: 1 GB", fb(1024**3) == "1 GB", fb(1024**3))
check("fmt: None", fb(None) == "\u2026", repr(fb(None)))
check("fmt: -5 -> 0 B", fb(-5) == "0 B", fb(-5))
check("fmt: 1234567890", fb(1234567890) == "1,15 GB", fb(1234567890))
check("fmt: 1 TB (Grenze)", fb(1024**4) == "1 TB", fb(1024**4))
check("fmt: 1 PB (Obergrenze)", fb(1024**5) == "1 PB", fb(1024**5))
check("count: 1234", tr.format_count(1234) == "1\u202f234", tr.format_count(1234))
check("count: None", tr.format_count(None) == "\u2026")

# --- 7. temp_definitions: Duplikat-Pruefung auf dieser Maschine ---
defs = tr.temp_definitions()
print("defs:", [(t, p) for t, p in defs])
r0 = os.path.realpath(defs[0][1])
r1 = os.path.realpath(defs[1][1])
print(f"realpath dup %TEMP%==%LOCALAPPDATA%\\Temp: {r0 == r1}")

# --- 8. realpath Case-Normalisierung (Windows: Dedup ist case-SICHER) ---
p = os.path.join(BASE, "Case")
os.makedirs(p)
same_dir_lower = p.lower()
check("realpath: wird auf On-Disk-Case normalisiert (Dedup case-sicher)",
      os.path.realpath(p) == os.path.realpath(same_dir_lower),
      f"{os.path.realpath(p)} vs {os.path.realpath(same_dir_lower)}")

# --- 9. _de / Randfaelle ---
check("_de: 0.5 -> '0,5'", tr._de(0.5) == "0,5", tr._de(0.5))
check("_de: 1.0 -> '1'", tr._de(1.0) == "1", tr._de(1.0))
check("_de: 1234.5 -> '1\u202f234,5'", tr._de(1234.5) == "1\u202f234,5", tr._de(1234.5))

# --- 10. Ellipsen ---
check("ellipsize: kurz", tr.TempApp._ellipsize("C:\\temp", 30) == "C:\\temp")
check("ellipsize: lang", tr.TempApp._ellipsize("x"*40, 30).endswith("\u2026"))

# --- 11. time_ago (ohne Tk: Instanzmethode -> Mock) ---
import types
t = types.MethodType(tr.TempApp._time_ago, object.__new__(type("X", (), {})))
ts = time.time() - 5
check("time_ago: 5s", t(ts) == "vor 5 Sekunden", t(ts))
check("time_ago: 61s -> 1 Minute", t(time.time()-61) == "vor 1 Minute")
check("time_ago: 3600s -> 1 Stunde", t(time.time()-3600) == "vor 1 Stunde")
check("time_ago: None", t(None) == "")

# --- 12. make_tray_icon ---
img = tr.make_tray_icon()
check("tray icon: 64x64 RGBA", img.size == (64, 64) and img.mode == "RGBA")

# --- 13. Symlink-auf-Ordner: Link weg, ZIEL bleibt unangetastet ---
# (Symlinks erfordern auf Windows Developer Mode/Admin -> bedingt)
link_target = os.path.join(BASE, "link_target")
os.makedirs(os.path.join(link_target, "inner"))
wf(os.path.join(link_target, "inner", "x.txt"), 50)
link_top = os.path.join(BASE, "linktop")
os.makedirs(link_top)
try:
    os.symlink(link_target, os.path.join(link_top, "lnk"))
    f4, d4, s4 = tr.delete_folder_contents(link_top)
    check("symlink: Link entfernt", not os.path.islink(os.path.join(link_top, "lnk")))
    check("symlink: Ziel unangetastet",
          os.path.exists(os.path.join(link_target, "inner", "x.txt")))
except (OSError, ValueError) as e:
    print(f"SKIP  symlink-Test (Symlinks nicht erlaubt: {e})")

# --- 14. Konflikt: zweiter Delete-Lauf ueberschneidet sich nicht (sequenziell) ---
f3, d3, s3 = tr.delete_folder_contents(root)  # erster Lauf hat alles weg
check("delete2: 2. Lauf findet nichts", f3 == 0 and d3 == 0 and s3 == 0,
      f"freed={f3} deleted={d3} skipped={s3}")

# --- 15. Junction (mklink /J): Link-Eintrag weg, Ziel NUR NICHT beruehrt ---
# Regressions-Test gegen den H1-Bug: os.path.islink() erkennt Junctions auf
# Windows NICHT -> os.walk lief durch sie und delete loeschte die ZIEL-inhalte.
# mklink /J funktioniert ohne Admin/Dev-Mode (im Gegensatz zu echten Symlinks).
import subprocess
j_tgt = os.path.join(BASE, "j_tgt"); os.makedirs(os.path.join(j_tgt, "inner"))
wf(os.path.join(j_tgt, "inner", "x.txt"), 50)
j_top = os.path.join(BASE, "j_top"); os.makedirs(j_top)
_jr = subprocess.run(["cmd", "/c", "mklink", "/J",
                      os.path.join(j_top, "jnk"), j_tgt],
                     capture_output=True, text=True)
_jnk = os.path.join(j_top, "jnk")
if os.path.isdir(_jnk):
    check("junction: _is_reparse_point erkennt Junction (islink tut das NICHT)",
          tr._is_reparse_point(_jnk) is True and os.path.islink(_jnk) is False,
          f"is_reparse={tr._is_reparse_point(_jnk)} islink={os.path.islink(_jnk)}")
    t5, c5 = tr.scan_folder(j_top)
    check("junction: scan laeuft NICHT durch Ziel (count=0, total=0)",
          c5 == 0 and t5 == 0, f"total={t5} count={c5}")
    f5, d5, s5 = tr.delete_folder_contents(j_top)
    check("junction: Link-Eintrag entfernt", not os.path.lexists(_jnk))
    check("junction: Ziel unangetastet (Datei existiert noch)",
          os.path.exists(os.path.join(j_tgt, "inner", "x.txt")))
    check("junction: deleted=1 (nur der Link-Eintrag)", d5 == 1, f"deleted={d5}")
    check("junction: skipped=0", s5 == 0, f"skipped={s5}")
else:
    print(f"SKIP junction-Test (mklink /J fehlgeschlagen: "
          f"{(_jr.stderr or _jr.stdout).strip()})")

# --- 16. Gesperrte Datei (Handle OHNE DELETE-Share) -> skipped-Pfad ---
# Windows: Loeschen fuehrt nur mit FILE_SHARE_DELETE; Handle mit nur
# FILE_SHARE_READ blockiert os.remove -> PermissionError -> skipped += 1.
import ctypes
k32 = ctypes.windll.kernel32
k32.CreateFileW.restype = ctypes.c_void_p
lk_dir = os.path.join(BASE, "lk"); os.makedirs(lk_dir)
lk_file = os.path.join(lk_dir, "locked.txt")
wf(lk_file, 42)
GENERIC_READ, FILE_SHARE_READ, OPEN_EXISTING = 0x80000000, 0x1, 3
h = k32.CreateFileW(lk_file, GENERIC_READ, FILE_SHARE_READ, None,
                    OPEN_EXISTING, 0, None)
if h is not None and h != ctypes.c_void_p(-1):
    f6, d6, s6 = tr.delete_folder_contents(lk_dir)
    check("locked: gesperrte Datei uebersprungen (skipped=1)",
          s6 == 1, f"skipped={s6} deleted={d6} freed={f6}")
    check("locked: Datei existiert noch", os.path.exists(lk_file))
    check("locked: freed=0 (nichts entfernt)", f6 == 0, f"freed={f6}")
    k32.CloseHandle(h)
    f7, d7, s7 = tr.delete_folder_contents(lk_dir)
    check("locked: nach Handle-Close wird sie geloest",
          not os.path.exists(lk_file), f"deleted={d7} skipped={s7}")
else:
    print("SKIP locked-Test (CreateFileW fehlgeschlagen, "
          f"LastError={ctypes.GetLastError()})")

print()
fails = [r for r in results if not r[1]]
print(f"ERGBNIS: {len(results)-len(fails)}/{len(results)} PASS, {len(fails)} FAIL")
# aufraeumen (read-only bits loesen, falls vorhanden)
for d in (ro_dir,):
    if os.path.isdir(d):
        os.chmod(d, stat.S_IWRITE | stat.S_IREAD)
shutil.rmtree(BASE, ignore_errors=True)
sys.exit(1 if fails else 0)
