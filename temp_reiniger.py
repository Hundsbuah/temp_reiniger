# -*- coding: utf-8 -*-
"""
TEMP-REINIGER — Windows-Tool für drei Temp-Ordner (CustomTkinter, Single-EXE)
============================================================================

DESIGN-VERTRAG (impeccable / frontend-design)
--------------------------------------------

THESIS
  Ein Temp-Ordner-Reiniger, der die *Gewichtung* der drei Windows-
  Temp-Ordner in den Vordergrund stellt — bewusst NICHT die graue
  WinForms-Liste mit roten Lösch-Buttons und NICHT das over-designed
  Neon-Dashboard. Die drei Ordner lesen sich wie drei Instrument-Felder.

OWN-WORLD
  Helles, kühles Slate (nicht Creme), matte weiße Karten, ein klares
  Teal-Akzent (kein Glow), industrielle Bahnschrift-Ziffern, mono Pfade
  (Consolas), Segoe UI für Text. Keine Broadsheet-Haarlinien.

STORY
  Der Nutzer sieht sofort, welcher Temp-Ordner am schwersten ist
  (Füllstand relativ zum größten), wie viel darin liegt, und leert gezielt
  oder alles. Nach dem Leeren sinken Zahl und Füllstand.

FIRST VIEWPORT
  Kopfzeile (Wortmarke links; rechts „Aktualisieren"-Refresh + Status-Punkt).
  Darunter drei gleiche
  Karten nebeneinander: Titel (Env-Token), Pfad (mono), große Zahl,
  Füllstand-Leiste, Dateizahl, Lösch-Button. Darunter eine Gesamt-Zeile
  über alle drei: großes Gesamt-Label links, großer „Alle löschen"-Button
  rechts. Fußzeile: Status.

FORM
  „The Scale" — drei Instrument-Felder mit relativen Füllstand-Leisten und
  großen Bahnschrift-Zahlen. Signiert durch Füllstand + Ziffer.

FINISH
  unreviewed and undocumented is unfinished; this build ends with the
  finish review, the verdict, DESIGN.md, and every shipping raster
  carrying its provenance.

SICHERHEIT
  - Es wird beim Start NIE automatisch gelöscht.
  - Löschen erfolgt nur durch explizite Auswahl: Button (zwei Schritte) oder
    Tray-Menü (Rechtsklick-Items; Linksklick = "Fenster öffnen", NICHT
    destruktiv).
  - JEDER Temp-Pfad wird vor Scan/Delete validiert (validate_temp_path):
    absolut, kein Laufwerksroot/UNC, letzte Komponente endet auf "temp".
    Verstoßende Karten werden unsicher markiert: kein Scan, kein Löschen.
    (Env-Variablen wie %TEMP% sind von außen setzbar und werden NICHT blind
    vertraut.)
  - Wurzelmappen selbst werden NIE gelöscht — nur deren Inhalt.
  - Reparse-Points (Symlinks/Junctions) IM BAUM werden nie gefolgt: der
    Link-Eintrag wird entfernt, das Ziel bleibt unangetastet (Reparse-
    Point-Prüfung, nicht nur islink: os.path.islink() erkennt auf Windows
    Junctions NICHT). EINSCHRÄNKUNG: Der KARTEN-Pfad wird vorher per
    os.path.realpath() aufgelöst — zeigt %TEMP% selbst auf einen Junction,
    wird das ZIEL geleert (die Karten-Root-Prüfung in
    delete_folder_contents greift dann nicht mehr).
  - Gesperrte Dateien werden übersprungen (kein Abbruch).
  - Minimieren/schließen -> Fenster in den System-Tray; dort per Rechtsklick
    die 4 Lösch-Optionen + "Fenster öffnen" + "Beenden". Ist das Tray-Icon
    nachweislich nicht verfügbar (1-s-Health-Check), wird degradiert:
    Schließen beendet dann die App (mit Status-Hinweis).
  - Single-Instance: eine zweite Instanz wird per benanntem Mutex abgelehnt.
"""

import os
import stat
import sys
import queue
import time
import ctypes
import threading
import traceback
import tkinter as tk
import tkinter.messagebox as tk_messagebox
import customtkinter as ctk

# --------------------------------------------------------------------------- #
#  Version
# --------------------------------------------------------------------------- #
__version__ = "1.3.0"

# --------------------------------------------------------------------------- #
#  Design-Token
# --------------------------------------------------------------------------- #
BG        = "#E9EDF3"   # kühles Slate (Fenster)
CARD      = "#FFFFFF"   # Kartenfläche
CARD_LINE = "#D9E0EA"   # Karten-Border
INK       = "#141A24"   # Haupttext (tiefe Slate)
INK_SOFT  = "#5E6B7D"   # gedämpfter Text
INK_FAINT = "#93A0B0"   # sehr gedämpft (Pfade)
ACCENT    = "#1296B0"   # frisches Teal (Aktion / Füllstand)
ACCENT_D  = "#0C7285"   # Teal hover
TRACK     = "#DCE6EC"   # Füllstand-Schiene
OK        = "#2E9E5B"   # Status: bereit / entfernt
WARN      = "#C9701E"   # Status: übersprungen / Bestätigung

THIN_SPACE = "\u202f"   # dürrer Abstand für Tausender
DOT        = "\u25CF"   # ●


# --------------------------------------------------------------------------- #
#  Formathilfen (deutsches Zahlformat)
# --------------------------------------------------------------------------- #
def _de(value, decimals=2):
    """Zahl im deutschen Format: Tausender-Dürrraum, Dezimalkomma."""
    s = f"{value:,.{decimals}f}".replace(",", THIN_SPACE).replace(".", ",")
    if "," in s:
        head, dec = s.rsplit(",", 1)
        dec = dec.rstrip("0")
        s = head + ("," + dec if dec else "")
    return s


def format_bytes(n):
    """Byte-Größe als lesbare Zeichenfolge (deutsche Konvention).

    FLOOR-Regel: die Einheit wird so gewählt, dass der ANGEZEIGTE Wert (auf
    2 Dezimalen) immer < 1024 bleibt — z. B. 1048575 B -> "1 MB" statt
    "1 024 KB". Einheiten sind nicht bei PB gedeckelt (EB/ZB/YB darüber).
    """
    if n is None:
        return "…"
    if n < 0:
        n = 0
    if n < 1024:
        return f"{int(n)} B"
    units = ["KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    v = float(n)
    i = -1
    while v >= 1024 and i < len(units) - 1:
        v /= 1024.0
        i += 1
    # Rundung darf keine 1024 im aktuellen Einheitenfeld erzeugen
    if i < len(units) - 1 and round(v, 2) >= 1024:
        v /= 1024.0
        i += 1
    return f"{_de(v, 2)} {units[i]}"


def format_count(n):
    if n is None:
        return "…"
    return f"{int(n):,}".replace(",", THIN_SPACE)


def _plural_de(n, eins, viele):
    """Deutsche Pluralwahl: 1 -> Singular, sonst Plural."""
    return eins if int(n) == 1 else viele


# --------------------------------------------------------------------------- #
#  Datei-Logik (nur lesen / löschen von INHALT, nie die Wurzel)
# --------------------------------------------------------------------------- #
def _is_reparse_point(path):
    """True, wenn `path` ein Reparse-Point ist: Symlink ODER Junction.

    WICHTIG: os.path.islink() erkennt auf Windows echte Symlinks, aber
    JUNCTIONS (Mount-Point-Reparse-Points) NICHT — os.walk() läuft trotzdem
    durch sie (das Ziel würde sonst mitgescannt/ gelöscht werden). Deshalb
    direkt FILE_ATTRIBUTE_REPARSE_POINT (0x400) prüfen. lstat (nicht stat!),
    damit die ATTRIBUTES des Links selbst und nicht des Ziels gelesen werden.
    """
    if os.path.islink(path):
        return True
    try:
        return bool(os.lstat(path).st_file_attributes & 0x400)
    except (AttributeError, OSError):
        return False


def _win_raw(p):
    """`\\?\\`-präfixierten absoluten Pfad (Windows-Long-Path-Form).

    Ohne das Präfix streckt der Kernel hostile Namen (NUL, trailing
    Dot/Space) oder routet sie auf Geräte — mit Präfix zeigen lstat/remove
    auf den echten Eintrag. Niemals doppelt prefixen.
    WICHTIG: Absolute Pfade NICHT normalisieren — os.path.abspath() streicht
    auf CPython 3.14 das trailing Dot weg ("F:\\x\\dot." -> "F:\\x\\dot")
    und würde den hostile Eintrag damit wieder unsichtbar machen.
    """
    if p.startswith("\\\\?\\"):
        return p
    if os.path.isabs(p):
        return "\\\\?\\" + p
    return "\\\\?\\" + os.path.abspath(p)


def _under_blocked(dp, blocked_dirs):
    """True, wenn `dp` selbst oder EINE TIEFERE Ebene eine bereits gezählte
    übersprungene Datei enthält (dann ist ein rmdir-Fehlschlag in `dp` nur
    Kaskade "nicht leer" und zählt NICHT zusätzlich als übersprungen)."""
    prefix = dp + os.sep
    return any(b == dp or b.startswith(prefix) for b in blocked_dirs)


def scan_folder(path):
    """(Größe in Byte, Dateianzahl, nicht lesbare Ordner) eines Ordners zählen.

    `blocked` zählt Ordner, die nicht eingelesen werden konnten (z. B.
    fehlende Rechte) — deren INHALT wird weder gezählt noch gelöscht; der
    Aufrufer meldet das sichtbar (Status amber). Fehlender Pfad -> (0, 0, 0).
    Reparse-Points (Symlinks/Junctions) werden NICHT gefolgt: ihr Ziel zählt
    nicht mit (prunen via dirnames, damit os.walk nicht hineinläuft).
    Hostile Namen (NUL, trailing Dot/Space) werden per `\\?\\`-Retry gezählt.
    Auch ein am scandir gescheiterter ORDNER (hostile Ordner-Namen) wird per
    `\\?\\`-Recovery nachgezählt — kein Phantom-„nicht lesbar".
    """
    total, count, blocked = 0, 0, 0
    if not path or not os.path.isdir(path):
        return 0, 0, 0
    unreadable = []   # gescheiterte Ordner (hostile Namen -> per `\\?\` lesbar)

    def _onerror(e):
        nonlocal blocked
        blocked += 1
        fn = getattr(e, "filename", None)
        if isinstance(fn, str) and fn:
            unreadable.append(fn)

    for dirpath, dirnames, filenames in os.walk(path, onerror=_onerror):
        dirnames[:] = [d for d in dirnames
                       if not _is_reparse_point(os.path.join(dirpath, d))]
        for name in filenames:
            fp = os.path.join(dirpath, name)
            st = None
            try:
                st = os.lstat(fp)
            except OSError:
                # ohne `\\?\`-Prefix scheitert lstat an hostile Namen
                try:
                    st = os.lstat(_win_raw(fp))
                except OSError:
                    pass
            if st is not None:
                total += st.st_size
                count += 1
    # `\\?\`-Recovery (L2-Fix 2026-10-17): ein am normalen scandir
    # gescheiterter Ordner ist unter dem Long-Path-Präfix oft sehr wohl
    # enumerable (hostile Namen) — sein Inhalt zählt dann doch mit.
    # handled/pending: ein verschachtelter gescheiterter Ordner wird genau
    # EINMAL behandelt (der Parent-Raw-Walk hat ihn schon gezählt).
    handled, pending = set(), {_win_raw(d) for d in unreadable}

    def _recover_scan(dp):
        nonlocal total, count, blocked
        raw = _win_raw(dp)

        def _err(e):
            nonlocal blocked
            if getattr(e, "filename", None) == raw:
                return               # Top: vom Haupt-Walk bereits gezählt
            blocked += 1             # nicht lesbarer Unterordner IM RAW-Subtree

        for dirpath, dirnames, filenames in os.walk(raw, topdown=True,
                                                    onerror=_err):
            handled.add(dirpath)
            if dirpath in pending:
                pending.discard(dirpath)
                blocked -= 1         # unter `\\?\` lesbar -> nicht mehr blockiert
            dirnames[:] = [d for d in dirnames
                           if not _is_reparse_point(os.path.join(dirpath, d))]
            for name in filenames:
                try:
                    st = os.lstat(os.path.join(dirpath, name))
                except OSError:
                    continue
                total += st.st_size
                count += 1

    for dp in unreadable:
        raw = _win_raw(dp)
        if raw in handled or not os.path.lexists(raw):
            continue
        _recover_scan(dp)
    return total, count, blocked


def delete_folder_contents(top):
    """Nur den INHALT von `top` löschen. `top` selbst bleibt bestehen.

    Rückgabe: (freier Byte, gelöschte Einträge, übersprungene Einträge,
    nicht lesbare Ordner).
    Sperrungen (in Benutzung / keine Rechte) werden übersprungen; ein
    BLOCKIERTER SUBTREE zählt genau EINMAL (die tiefste gezählte Ebene —
    i. d. R. die gesperrte Datei selbst), nicht zusätzlich jede nicht-leere
    Elternebene. `blocked` zählt Ordner ohne Leserecht (Inhalt unverfügbar).
    Reparse-Points (Symlinks ODER Junctions) werden nie gefolgt: der
    Link-Eintrag wird als Eintrag entfernt, das Ziel bleibt unangetastet.
    os.path.islink() erkennt Junctions auf Windows NICHT — deshalb
    _is_reparse_point(). Eine WURZEL, die selbst ein Link/Junction ist,
    wird nicht angefasst (Ziel wäre unbekannt).
    Ein am scandir gescheiterter Unterordner (hostile Ordner-Namen) wird per
    `\\?\\`-Recovery mitsamt Inhalt entfernt (L2-Fix 2026-10-17).
    """
    top = os.path.abspath(top)
    freed = deleted = skipped = blocked = 0
    if not os.path.isdir(top):
        return 0, 0, 0, 0
    if _is_reparse_point(top):
        return 0, 0, 0, 0
    # WICHTIG: topdown=True + in-place-Pruning der dirnames. os.walk läuft
    # auf Windows durch Junctions (is_symlink()==False) — nur ein PRUNE
    # verhindert, dass es in das Ziel hineingeht. (topdown=False wäre zu
    # spät: die Kinder — d. h. die ZIEL-Inhalte — kämen zuerst.)
    # Echte Ordner werden erst im 2. Durchgang bottom-up rmdir'ed
    # (topdown=True: beim Besuch wären die Kinder noch da).
    to_rmdir = []
    blocked_dirs = set()   # Ebenen mit mindestens einer übersprungenen DATEI
    unreadable = []        # gescheiterte Ordner (per `\\?\` rekonstruierbar)

    def _onerror(e):
        nonlocal blocked
        blocked += 1
        fn = getattr(e, "filename", None)
        if isinstance(fn, str) and fn:
            unreadable.append(fn)

    for dirpath, dirnames, filenames in os.walk(top, topdown=True,
                                                onerror=_onerror):
        keep = []
        for d in dirnames:
            dp = os.path.join(dirpath, d)
            if _is_reparse_point(dp):
                # Link-EINTRAG entfernen; os.rmdir trifft nur den Link,
                # nie das Ziel (empirisch verifiziert). `\\?\\`-Retry für
                # hostile Link-Namen.
                try:
                    try:
                        os.rmdir(dp)
                    except OSError:
                        os.rmdir(_win_raw(dp))
                    deleted += 1
                except OSError:
                    skipped += 1
            else:
                keep.append(d)
        dirnames[:] = keep
        for name in filenames:
            fp = os.path.join(dirpath, name)
            st = None
            try:
                st = os.lstat(fp)
            except OSError:
                # hostile Namen (NUL, trailing Dot/Space): ohne `\\?\\`
                # streckt der Kernel den Namen — Retry mit Long-Path-Form
                try:
                    st = os.lstat(_win_raw(fp))
                except OSError:
                    pass
            if st is None:
                skipped += 1
                blocked_dirs.add(dirpath)
                continue
            try:
                try:
                    os.remove(fp)
                except PermissionError:
                    # Windows: read-only-Datei -> Write-Bit setzen und erneut löschen
                    try:
                        os.chmod(fp, stat.S_IWRITE)
                        os.remove(fp)
                    except OSError:
                        raise
                freed += st.st_size
                deleted += 1
            except (PermissionError, OSError):
                # letzte Rettung für hostile Namen: `\\?\\`-Pfad löschen
                try:
                    os.remove(_win_raw(fp))
                    freed += st.st_size
                    deleted += 1
                except OSError:
                    skipped += 1
                    blocked_dirs.add(dirpath)
        if dirpath != top:
            to_rmdir.append(dirpath)

    # `\\?\`-Recovery VOR dem rmdir-Pfad (L2-Fix 2026-10-17): ein am normalen
    # scandir gescheiterter Ordner (hostile Namen: trailing Dot/Space) ist
    # unter dem Long-Path-Präfix voll zugänglich — Inhalt löschen und den
    # Ordner selbst entfernen (dann ist sein Parent wieder leer).
    # handled/pending: ein verschachtelter gescheiterter Ordner wird genau
    # EINMAL behandelt (der Parent-Raw-Walk hat ihn schon enumerated) und
    # zählt dann nicht mehr als „blockiert".
    handled, pending = set(), {_win_raw(d) for d in unreadable}

    def _recover_hostile(dp):
        nonlocal freed, deleted, skipped, blocked
        raw = _win_raw(dp)

        def _err(e):
            nonlocal blocked
            if getattr(e, "filename", None) == raw:
                return                  # Top: vom Haupt-Walk bereits gezählt
            blocked += 1                # nicht lesbarer Unterordner IM RAW-Subtree

        sub = []
        for dirpath, dirnames, filenames in os.walk(raw, topdown=True,
                                                    onerror=_err):
            handled.add(dirpath)
            if dirpath in pending:
                pending.discard(dirpath)
                blocked -= 1            # unter `\\?\` lesbar -> Zählung zurück
            keep = []
            for d in dirnames:
                dpp = os.path.join(dirpath, d)
                if _is_reparse_point(dpp):
                    try:
                        os.rmdir(dpp)   # dpp ist bereits `\\?\`-Form
                        deleted += 1
                    except OSError:
                        skipped += 1
                else:
                    keep.append(d)
            dirnames[:] = keep
            for name in filenames:
                fp = os.path.join(dirpath, name)
                try:
                    st = os.lstat(fp)
                except OSError:
                    skipped += 1
                    continue
                try:
                    try:
                        os.remove(fp)
                    except PermissionError:
                        os.chmod(fp, stat.S_IWRITE)
                        os.remove(fp)
                    freed += st.st_size
                    deleted += 1
                except OSError:
                    skipped += 1
            if dirpath != raw:
                sub.append(dirpath)
        # bottom-up, danach der gescheiterte Ordner selbst (er ist Inhalt
        # SEINES PARENTS). Bleibt er übrig, zählt er als übersprungen (er ist
        # lesbar — die blocked-Zählung wurde oben zurückgenommen).
        for dirpath in sorted(sub, key=len, reverse=True):
            try:
                os.rmdir(dirpath)
            except FileNotFoundError:
                pass
            except OSError:
                skipped += 1
        try:
            os.rmdir(raw)
        except FileNotFoundError:
            pass
        except OSError:
            skipped += 1

    for dp in unreadable:
        raw = _win_raw(dp)
        if raw in handled or not os.path.lexists(raw):
            continue
        _recover_hostile(dp)

    # 2. Durchgang: bottom-up (tiefere Pfade sind länger) — jetzt sind alle
    # Inhalte weg, die Ordner sind leer. Wurzel bleibt immer stehen.
    # Ein rmdir-Fehlschlag zählt NUR, wenn die Blockade HIER beginnt: liegt
    # tiefer eine bereits gezählte übersprungene Datei ODER eine bereits
    # gezählte nicht entfernbare Ordner-Ebene, ist das hier nur Kaskade
    # ("nicht leer") und zählt NICHT zusätzlich (N2-Fix + L3-Fix 2026-10-17:
    # reine Ordner-Kaskaden zählten vorher pro Ebene).
    for dirpath in sorted(to_rmdir, key=len, reverse=True):
        try:
            os.rmdir(dirpath)
        except FileNotFoundError:
            pass                        # war schon entfernt
        except PermissionError:
            # Windows: read-only-Ordner -> Write-Bit setzen und erneut entfernen
            try:
                os.chmod(dirpath, stat.S_IWRITE)
                os.rmdir(dirpath)
            except OSError:
                if not _under_blocked(dirpath, blocked_dirs):
                    skipped += 1        # hier blockiert -> zählt mit
                blocked_dirs.add(dirpath)   # Ahnen-Ebenen = Kaskade, zählt nicht
        except OSError:
            if not _under_blocked(dirpath, blocked_dirs):
                skipped += 1            # hier blockiert -> zählt mit
            blocked_dirs.add(dirpath)   # Ahnen-Ebenen = Kaskade, zählt nicht
    return freed, deleted, skipped, blocked


# --------------------------------------------------------------------------- #
#  Temp-Ordner-Definition (genau drei, wie gefordert)
# --------------------------------------------------------------------------- #
def temp_definitions():
    defs = [
        ("%TEMP%",              os.path.expandvars("%TEMP%")),
        ("%LOCALAPPDATA%\\Temp", os.path.expandvars("%LOCALAPPDATA%\\Temp")),
        ("%SystemRoot%\\Temp",   os.path.expandvars("%SystemRoot%\\Temp")),
    ]
    return defs


# --------------------------------------------------------------------------- #
#  Pfad-Validierung + Fehler-Log
# --------------------------------------------------------------------------- #
def validate_temp_path(raw):
    """(ok, Grund) für einen expandierten Temp-Pfad, VOR Scan/Delete.

    Env-Variablen sind von außen setzbar (z. B. %TEMP%=C:\\Windows oder
    %TEMP%=.) — die App darf nicht blind darauf vertrauen. Zulässig:
    absoluter lokaler Pfad (kein UNC), kein Laufwerksroot, dessen letzte
    Komponente auf "temp" endet (deckt "Temp", "WindowsTemp" & Co. ab;
    schließt "C:\\Windows", "C:\\Users" & Co. aus). Relativer Pfad /
    leerer Wert / nicht-expanded Token -> abgelehnt (Karte wird unsicher).
    ACHTUNG (bewusste Einschränkung, s. Modul-Docstring): realpath löst
    Junctions auf — die Suffix-Prüfung läuft auf dem aufgelösten ZIEL.
    """
    if not raw:
        return False, "Pfad leer"
    if raw.startswith("\\\\") or raw.startswith("//"):
        return False, "Netzpfad abgelehnt"
    if not os.path.isabs(raw):
        return False, "relativer Pfad abgelehnt"
    try:
        resolved = (os.path.realpath(raw) if os.path.isdir(raw)
                    else os.path.abspath(raw))
    except OSError:
        return False, "Pfad nicht auflösbar"
    if os.path.dirname(resolved) == resolved:
        return False, "Laufwerksroot abgelehnt"
    if not os.path.basename(resolved).lower().endswith("temp"):
        return False, "kein Temp-Ordner"
    return True, ""


def _log_error(where, exc_text):
    """Fehlerdetails nach %LOCALAPPDATA%\\Temp-Reiniger\\error.log (best-effort).

    In der windowed EXE ist sys.stderr None: traceback.print_exc() ist dort
    ein stilles No-Op (und in CPython <= 3.13 würde es im traceback-Modul
    selbst noch werfen). Das Log-File ist der verlässliche Ort für Details.
    """
    try:
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        d = os.path.join(base, "Temp-Reiniger")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "error.log"), "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [{where}]\n"
                    f"{exc_text}\n")
    except Exception:
        pass


def make_tray_icon():
    """Tray-Icon (PIL): Teal-Platte mit weißem Papierkorb (64x64)."""
    from PIL import Image, ImageDraw
    S = 64
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([2, 2, 61, 61], radius=14, fill=(18, 150, 176, 255))
    d.rectangle([14, 20, 50, 27], fill=(255, 255, 255, 255))      # Deckel
    d.rectangle([28, 13, 36, 20], fill=(255, 255, 255, 255))      # Griff
    d.polygon([(18, 31), (46, 31), (42, 54), (22, 54)],
              fill=(255, 255, 255, 255))                          # Korpus
    for x in (28, 32, 36):
        d.line([(x, 36), (x, 50)], fill=(18, 150, 176, 255), width=2)
    return img


# --------------------------------------------------------------------------- #
#  Kleines Tooltip (voller Pfad auf Hover)
# --------------------------------------------------------------------------- #
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _e):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 16
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip, text=self.text, font=("Consolas", 9),
            bg=INK, fg="#FFFFFF", padx=9, pady=5,
        ).pack()

    def _hide(self, _e):
        self.hide()

    def hide(self):
        """Tooltip zerstören (auch programmatisch, z. B. beim Ausblenden des
        Hauptfensters — das overrideredirect-Toplevel würde sonst schweben)."""
        if self.tip:
            self.tip.destroy()
            self.tip = None


# --------------------------------------------------------------------------- #
#  Anwendung
# --------------------------------------------------------------------------- #
class TempApp(ctk.CTk):
    def __init__(self, initial_scan=True):
        super().__init__()
        self._closing = False
        self._busy = False
        self._tween_tokens = {}
        self._tween_last = {}      # Key -> zuletzt ANGEZEIGTER Tween-Wert
        self._tween_jobs = {}      # Key -> laufender after()-Job (Quit-Cancel)
        self._ticker_job = None    # after()-Ids der Selbst-Treiber (D4-Fix)
        self._poll_job = None
        self._poll_active = False  # Reentrancy-Schutz _poll_ui (M2-Fix)
        self._all_armed = False
        self._all_armed_job = None
        self._last_scan_ts = None
        self._last_scan_str = None
        self._last_total = None
        self._status_mode = None
        self._rescan_job = None
        self._ui_queue = queue.Queue()   # Main-Thread-Kommandos (Tray + Worker-Callbacks)
        self._tray_icon = None
        self._tray_ready = False
        self._tray_active = False
        self._tray_started = None      # monotonic-Zeitpunkt Tray-Thread-Start
        self._tray_degraded_hint = False   # Degradations-Hinweis schon gezeigt?

        ctk.set_appearance_mode("Light")
        self.title(f"Temp-Reiniger {__version__}")
        self._center(self, 1060, 600)
        self.minsize(920, 540)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Unmap>", self._on_unmap)

        # Fonts (native Windows-Schriftarten; Fallback automatisch)
        self.f_title = ctk.CTkFont(family="Bahnschrift", size=16, weight="bold")
        self.f_wordmark = ctk.CTkFont(family="Bahnschrift", size=15, weight="bold")
        self.f_num = ctk.CTkFont(family="Bahnschrift", size=30, weight="bold")
        self.f_total = ctk.CTkFont(family="Bahnschrift", size=44, weight="bold")
        self.f_path = ctk.CTkFont(family="Consolas", size=11)
        self.f_body = ctk.CTkFont(family="Segoe UI", size=12)
        self.f_btn = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.f_small = ctk.CTkFont(family="Segoe UI", size=11)

        self._build_ui()
        if initial_scan:
            self._scan_all()   # beim Start nur einlesen — niemals löschen
        self._status_ticker()
        self._start_tray()
        self._poll_ui()

    # ------------------------------------------------------------- layout
    def _center(self, win, w, h):
        """Zentrieren über den gesamten VIRTUELLEN Schreibtisch (Multi-Monitor),
        nicht nur über den Primärmonitor. Fallback: Primärmonitor."""
        x0, y0 = 0, 0
        vw, vh = win.winfo_screenwidth(), win.winfo_screenheight()
        try:
            user32 = ctypes.windll.user32
            vw = user32.GetSystemMetrics(78)   # SM_CXVIRTUALSCREEN
            vh = user32.GetSystemMetrics(79)   # SM_CYVIRTUALSCREEN
            x0 = user32.GetSystemMetrics(76)   # SM_XVIRTUALSCREEN
            y0 = user32.GetSystemMetrics(77)   # SM_YVIRTUALSCREEN
        except Exception:
            pass
        x = max(x0, x0 + (vw - w) // 2)
        y = max(y0, y0 + (vh - h) // 2 - 40)
        win.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        root = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        root.pack(fill="both", expand=True)
        root.grid_columnconfigure((0, 1, 2), weight=1, uniform="c")
        root.grid_rowconfigure(1, weight=1)

        self._build_header(root)
        self.cards = []
        for i, (title, path) in enumerate(temp_definitions()):
            self._build_card(root, i, title, path)
        self._build_total(root)
        self._build_status(root)

    def _build_header(self, root):
        header = ctk.CTkFrame(root, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=3, sticky="ew",
                    padx=26, pady=(22, 8))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text=DOT, font=self.f_wordmark,
                     text_color=ACCENT).pack(side="left", padx=(0, 9))
        ctk.CTkLabel(left, text="TEMP-REINIGER", font=self.f_wordmark,
                     text_color=INK).pack(side="left")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")
        # Sekundäre Aktion: Temp-Größen neu einlesen / Ordner aktualisieren (kein Löschen)
        self.scan_button = ctk.CTkButton(
            right, text="Aktualisieren", font=self.f_body, height=32,
            fg_color="transparent", border_width=1, border_color=ACCENT,
            hover_color=TRACK, text_color=ACCENT, corner_radius=8,
            command=self._scan_all,
        )
        self.scan_button.pack(side="left", padx=(0, 14))
        self.status_dot = ctk.CTkLabel(right, text=DOT, font=self.f_small,
                                       text_color=OK)
        self.status_dot.pack(side="left", padx=(0, 7))
        self.status_head = ctk.CTkLabel(right, text="Bereit", font=self.f_body,
                                        text_color=INK_SOFT)
        self.status_head.pack(side="left")
        defs = temp_definitions()
        try:
            drives = sorted({os.path.splitdrive(os.path.realpath(p))[0]
                             for _, p in defs if p})
        except Exception:
            drives = []
        drive_txt = (" · ".join(d + "\\" for d in drives) + " · ") if drives else ""
        ctk.CTkLabel(right, text=f"{drive_txt}{len(defs)} Temp-Ordner",
                     font=self.f_small, text_color=INK_FAINT
                     ).pack(side="left", padx=(14, 0))

    def _build_card(self, root, idx, title, path):
        # H1-Fix: Env-Pfad validieren, BEVOR irgendwas an ihm gescannt/
        # gelöscht wird. Unsichere Karten werden markiert, nicht gescannt,
        # nicht gelöscht.
        safe, unsafe_reason = validate_temp_path(path)
        card = ctk.CTkFrame(root, fg_color=CARD, border_width=1,
                            border_color=CARD_LINE, corner_radius=14)
        card.grid(row=1, column=idx, sticky="nsew", padx=14, pady=14)
        for r in range(7):
            card.grid_rowconfigure(r, weight=0)
        card.grid_rowconfigure(5, weight=1)     # dehnbarer Zwischenraum

        # Titel (Env-Token)
        ctk.CTkLabel(card, text=title, font=self.f_title, text_color=INK,
                     anchor="w").grid(row=0, column=0, sticky="ew",
                                      padx=20, pady=(20, 0))
        # Pfad (mono, gekürzt; voller Pfad im Tooltip)
        full = path or "(nicht vorhanden)"
        if not safe:
            full = f"{full}\n⚠ Pfad unzulässig: {unsafe_reason}"
        shown = self._ellipsize(path or "(nicht vorhanden)", 30)
        path_lbl = ctk.CTkLabel(card, text=shown, font=self.f_path,
                                text_color=INK_FAINT, anchor="w")
        path_lbl.grid(row=1, column=0, sticky="ew", padx=20, pady=(2, 0))
        card_tooltip = Tooltip(path_lbl, full)

        # Große Zahl (unsichere Karte: dauerhaft "—")
        num = ctk.CTkLabel(card, text="…" if safe else "—", font=self.f_num,
                           text_color=INK, anchor="w")
        num.grid(row=2, column=0, sticky="ew", padx=20, pady=(16, 2))
        # Füllstand-Leiste
        bar = ctk.CTkProgressBar(card, fg_color=TRACK, progress_color=ACCENT,
                                 height=9, corner_radius=5)
        bar.set(0.0)
        bar.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 8))
        # Dateizahl
        count = ctk.CTkLabel(card, text="—" if safe else "unzulässig",
                             font=self.f_body,
                             text_color=INK_SOFT if safe else WARN,
                             anchor="w")
        count.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 2))

        # Lösch-Button (unsichere Karte: abgewertet, Klick gibt Feedback)
        if safe:
            btn = ctk.CTkButton(
                card, text="Temp löschen", font=self.f_btn, height=42,
                fg_color=ACCENT, hover_color=ACCENT_D, text_color="#FFFFFF",
                corner_radius=9, command=lambda i=idx: self._on_card_delete(i),
            )
        else:
            btn = ctk.CTkButton(
                card, text="Pfad unzulässig", font=self.f_btn, height=42,
                fg_color=TRACK, hover_color=TRACK, text_color=INK_FAINT,
                corner_radius=9,
                command=lambda i=idx: self._on_unsafe_card(i),
            )
        btn.grid(row=6, column=0, sticky="ew", padx=20, pady=(10, 20))

        self.cards.append({
            "idx": idx, "title": title, "path": path,
            "num": num, "bar": bar, "count": count, "button": btn,
            "tooltip": card_tooltip,
            "safe": safe, "unsafe_reason": unsafe_reason,
            "armed": False, "armed_job": None, "bytes": None, "nfiles": None,
        })

    def _on_unsafe_card(self, idx):
        """Klick auf dem Button einer unsicheren Karte: Feedback statt Stille."""
        if self._closing:
            return
        c = self.cards[idx]
        self._set_status(f"Pfad unzulässig: {c['unsafe_reason']} — "
                         "Löschen für diese Karte verweigert.", WARN)

    def _build_total(self, root):
        total = ctk.CTkFrame(root, fg_color=CARD, border_width=1,
                             border_color=CARD_LINE, corner_radius=14)
        total.grid(row=2, column=0, columnspan=3, sticky="ew",
                   padx=14, pady=(0, 14))

        inner = ctk.CTkFrame(total, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=22, pady=18)

        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(left, text="GESAMT · ALLE TEMP-ORDNER", font=self.f_small,
                     text_color=INK_SOFT).pack(anchor="w")
        self.total_num = ctk.CTkLabel(left, text="…", font=self.f_total,
                                      text_color=INK)
        self.total_num.pack(anchor="w", pady=(0, 2))
        self.total_note = ctk.CTkLabel(left, text="", font=self.f_small,
                                       text_color=WARN)
        self.total_note.pack(anchor="w")

        self.total_button = ctk.CTkButton(
            inner, text="Alle löschen", font=self.f_btn, height=54,
            width=230, fg_color=ACCENT, hover_color=ACCENT_D,
            text_color="#FFFFFF", corner_radius=10,
            command=lambda: self._on_all_delete(),
        )
        self.total_button.pack(side="right", anchor="center")

    def _build_status(self, root):
        bar = ctk.CTkFrame(root, fg_color="transparent")
        bar.grid(row=3, column=0, columnspan=3, sticky="ew",
                 padx=26, pady=(0, 18))
        self.status_msg = ctk.CTkLabel(bar, text="Bereit.", font=self.f_body,
                                       text_color=INK_SOFT, anchor="w")
        self.status_msg.pack(side="left")

    # ------------------------------------------------------------- helpers
    @staticmethod
    def _ellipsize(s, n):
        if len(s) <= n:
            return s
        return s[: n - 1] + "…"

    def _set_status(self, msg, color=INK_SOFT):
        self.status_msg.configure(text=msg, text_color=color)

    def _time_ago(self, ts):
        """Zeitstempel als „vor X Sekunden/Minuten/Stunden" (deutsch)."""
        if ts is None:
            return ""
        s = max(0, int(time.time() - ts))
        if s < 60:
            unit = "Sekunde" if s == 1 else "Sekunden"
            return f"vor {s} {unit}"
        m = s // 60
        if m < 60:
            unit = "Minute" if m == 1 else "Minuten"
            return f"vor {m} {unit}"
        h = m // 60
        unit = "Stunde" if h == 1 else "Stunden"
        return f"vor {h} {unit}"

    def _status_ticker(self):
        """Refresh-Feedback: aktualisiert „vor X Sekunden" (nur Bereit-
        Zustand) + 1-s Tray-Health-Check."""
        if self._closing:
            return
        self._tray_health()
        if self._status_mode == "ready" and self._last_scan_ts is not None:
            self._set_status(
                f"Bereit · eingelesen {self._last_scan_str} · "
                f"{self._time_ago(self._last_scan_ts)} · "
                f"{format_bytes(self._last_total)} gesamt"
            )
        self._ticker_job = self.after(1000, self._status_ticker)

    def _cancel_rescan(self):
        """Angehängten Auto-Rescan (nach Lösch-Aktion) abbrechen."""
        if getattr(self, "_rescan_job", None):
            try:
                self.after_cancel(self._rescan_job)
            except Exception:
                pass
            self._rescan_job = None

    def _schedule_rescan(self, delay_ms=3000):
        """Ordner nach Lösch-Aktion automatisch neu einscannen.

        Kurze Verzögerung, damit die freigemachte Größe (MB/GB) im Status
        sichtbar bleibt. Ein vorher angehängter Rescan wird ersetzt.
        """
        if self._closing:
            return
        self._cancel_rescan()
        def do():
            self._rescan_job = None
            if not self._closing:
                self._scan_all()
        self._rescan_job = self.after(delay_ms, do)

    def _set_busy(self, busy):
        self._busy = busy
        state = "disabled" if busy else "normal"
        for c in self.cards:
            c["button"].configure(state=state)
        self.total_button.configure(state=state)
        self.scan_button.configure(state=state)
        if busy:
            # Konsistenz: BEIDES disarmen — Karten UND "Alle löschen"-Arming
            # (sonst überlebt ein "stale" Arm-State den Scan und ein Klick
            # danach könnte mit alter Bestätigung alles löschen)
            self._all_armed = False
            if getattr(self, "_all_armed_job", None):
                try:
                    self.after_cancel(self._all_armed_job)
                except Exception:
                    pass
                self._all_armed_job = None
            self.total_button.configure(text="Alle löschen", fg_color=ACCENT,
                                        hover_color=ACCENT_D)
            for c in self.cards:
                self._disarm(c)

    def _disarm(self, c):
        if c["armed_job"]:
            try:
                self.after_cancel(c["armed_job"])
            except Exception:
                pass
            c["armed_job"] = None
        c["armed"] = False
        c["button"].configure(text="Temp löschen", fg_color=ACCENT,
                              hover_color=ACCENT_D)

    def _arm(self, c, label, ms=2600):
        """Zwei-Stufen-Bestätigung: Button kurz armieren."""
        c["armed"] = True
        c["button"].configure(text=label, fg_color=WARN, hover_color=WARN)
        def revert():
            if c["armed"]:
                self._disarm(c)
        c["armed_job"] = self.after(ms, revert)

    # ------------------------------------------------------------- Tween
    def _tween(self, key, from_v, to_v, apply, duration=420, done=None):
        token = self._tween_tokens.get(key, 0) + 1
        self._tween_tokens[key] = token
        steps = 18
        interval = max(8, round(duration / (steps + 1)))   # duration wird nun honoriert
        def step(i):
            if self._closing:
                return
            if self._tween_tokens.get(key) != token:
                return
            t = min(1.0, i / steps)
            e = 1 - (1 - t) ** 3            # ease-out
            v = from_v + (to_v - from_v) * e
            self._tween_last[key] = v       # zuletzt angezeigter Wert merken
            apply(v)
            if i < steps:
                self._tween_jobs[key] = self.after(interval,
                                                   lambda: step(i + 1))
            else:
                self._tween_last[key] = to_v
                apply(to_v)
                if done:
                    done()
        step(0)

    def _reset_tween(self, key):
        """Laufenden Tween für `key` abbrechen (Token erhöhen) und den
        zuletzt angezeigten Wert zurücksetzen — neue Scans starten dann
        sauber beim Placeholder (kein Überblenden durch alten Tween)."""
        self._tween_tokens[key] = self._tween_tokens.get(key, 0) + 1
        self._tween_last[key] = 0.0

    # ------------------------------------------------------------- Scan
    def _scan_all(self):
        self._set_busy(True)
        self._cancel_rescan()
        self._status_mode = "scanning"
        self.scan_button.configure(text="Aktualisiere …")
        self._set_status("Wird eingelesen …", INK_SOFT)
        self.status_dot.configure(text_color=WARN)
        self.status_head.configure(text="Liest …")
        for i, c in enumerate(self.cards):
            if not c["safe"]:
                continue        # unsichere Karte: bleibt "—", wird nicht gescannt
            self._reset_tween(f"bar{i}")
            self._reset_tween(f"num{i}")
            c["num"].configure(text="…")
            c["count"].configure(text="—")
            c["bar"].set(0.0)
        self._reset_tween("total")
        self.total_num.configure(text="…")
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        try:
            # Memo keyt nach REALPATH: auf Standard-Maschinen zeigen %TEMP% und
            # %LOCALAPPDATA%\Temp auf denselben Ordner -> sonst doppeltes Walken
            memo = {}
            for c in self.cards:
                if not c["safe"]:
                    continue    # unsichere Pfade werden NICHT gescannt
                p = c["path"]
                k = os.path.realpath(p) if p else p
                if k not in memo:
                    try:
                        memo[k] = scan_folder(p)
                    except Exception:
                        memo[k] = (0, 0, 0)
            payload = [(c["idx"], memo.get(os.path.realpath(c["path"]) if c["path"] else c["path"], (0, 0, 0)))
                       for c in self.cards if c["safe"]]
        except Exception:
            # M1-Fix: Sicherheitsnetz — ohne Completion-Callback würde die UI
            # für immer "busy" bleiben (realpath-Fehler o. Ä. inklusive).
            # In der console-less EXE ist print_exc() ein No-Op -> ins Log.
            if sys.stderr is not None:
                traceback.print_exc()
            _log_error("scan_worker", traceback.format_exc())
            self._ui_queue.put(self._on_scan_error)
            return
        # thread-sicher: Ergebnis in Queue legen, Main-Thread führt _on_scanned aus
        self._ui_queue.put(lambda: self._on_scanned(payload))

    def _scan_error_ui(self):
        """Scan fehlgeschlagen: UI wieder freigeben + Warnung (Main-Thread)."""
        if self._closing:
            return
        self._set_busy(False)
        self.scan_button.configure(text="Aktualisieren")
        self.status_head.configure(text="Fehler")
        self.status_dot.configure(text_color=WARN)
        self._status_mode = "result"   # Ticker lässt die Meldung stehen
        self._set_status(
            "Fehler beim Einlesen — Details: "
            "%LOCALAPPDATA%\\Temp-Reiniger\\error.log", WARN)

    def _on_scan_error(self):
        """Scan-Worker-Net: immer eine Completion-Callback (M1-Fix)."""
        self._scan_error_ui()

    def _on_scanned(self, payload):
        if self._closing:
            return
        try:
            blocked_total = 0
            for idx, (b, n, bl) in payload:
                c = self.cards[idx]
                c["bytes"], c["nfiles"] = b, n
                blocked_total += bl or 0
            # relative Füllstand (gröster Ordner = voll; nur sichere Karten)
            max_b = max([c["bytes"] or 0 for c in self.cards if c["safe"]],
                        default=0) or 1
            # Gesamt über EINDEUTIGE Ordner: Duplikate (z. B. %TEMP% ==
            # %LOCALAPPDATA%\Temp) nur einmal zählen — die Karten zeigen
            # trotzdem jeweils ihre eigene Größe. Unsichere Karten zählen
            # NICHT mit (sie werden auch nicht gescannt).
            _uniq = {}
            for c in self.cards:
                if c["safe"]:
                    _uniq[os.path.realpath(c["path"]) if c["path"]
                           else ("idx", c["idx"])] = c["bytes"] or 0
            total = sum(_uniq.values())
            # Duplikat-Hinweis (gleicher physischer Pfad, nur sichere Karten)
            paths = [os.path.realpath(c["path"]) if c["path"] else None
                     for c in self.cards if c["safe"]]
            dup = len(set(paths)) < len(paths)
            self.total_note.configure(
                text=("Hinweis: zwei Pfade zeigen auf denselben Ordner "
                      "(doppelt angezeigt, im Gesamt nur einmal gezählt).")
                if dup else ""
            )
            for i, c in enumerate(self.cards):
                if not c["safe"]:
                    continue
                frac = (c["bytes"] or 0) / max_b
                # Ausgangs-Wert = zuletzt ANGEZEIGTER Wert (kein Sprung, wenn ein
                # Tween unterbrochen wurde)
                prev_bar = float(self._tween_last.get(f"bar{i}", 0.0))
                prev_b = float(self._tween_last.get(f"num{i}", 0))
                self._tween(f"bar{i}", prev_bar, frac, c["bar"].set, 520 + i * 70)
                self._tween(f"num{i}", prev_b, float(c["bytes"] or 0),
                            lambda v, n=c["num"]: n.configure(text=format_bytes(int(v))),
                            520 + i * 70)
                c["count"].configure(text=f"{format_count(c['nfiles'])} "
                                          f"{_plural_de(c['nfiles'] or 0, 'Datei', 'Dateien')}")
            self._tween("total", float(self._tween_last.get("total", 0)), float(total),
                        lambda v: self.total_num.configure(text=format_bytes(int(v))),
                        560)
            # fertig
            self._set_busy(False)
            self.scan_button.configure(text="Aktualisieren")
            self._last_scan_ts = time.time()
            self._last_scan_str = time.strftime("%H:%M")
            self._last_total = total
            self._status_mode = "ready"
            self.status_head.configure(text="Bereit")
            status_txt = (f"Bereit · eingelesen {self._last_scan_str} · "
                          f"vor 0 Sekunden · {format_bytes(total)} gesamt")
            if blocked_total:
                # Teilsichtbarkeit: amber statt grün (es fehlt Etwas)
                status_txt += (f" · {format_count(blocked_total)} "
                               f"{_plural_de(blocked_total, 'Eintrag', 'Einträge')} "
                               f"nicht lesbar")
                self.status_dot.configure(text_color=WARN)
                self._set_status(status_txt, WARN)
            else:
                self.status_dot.configure(text_color=OK)
                self._set_status(status_txt, INK_SOFT)
        except Exception:
            # M1-Fix: auch der Main-Thread-Teil braucht ein Netz — sonst
            # könnte die UI nach einem Fehler hier "busy" bleiben (der
            # äußere Poller-Net fängt den Throw, weiß aber nicht, dass ein
            # Scan offen war).
            if sys.stderr is not None:
                traceback.print_exc()
            _log_error("on_scanned", traceback.format_exc())
            self._scan_error_ui()

    # ------------------------------------------------------------- Delete
    def _on_card_delete(self, idx):
        c = self.cards[idx]
        if self._busy:
            return
        if c["armed"]:
            self._disarm(c)
            self._do_delete({"idx": idx})
        else:
            self._arm(c, "Wirklich löschen?")

    def _on_all_delete(self):
        if self._busy:
            return
        if self._all_armed:
            self._all_armed = False
            self.total_button.configure(text="Alle löschen", fg_color=ACCENT,
                                        hover_color=ACCENT_D)
            self._do_delete({"all": True})
        else:
            self._all_armed = True
            self.total_button.configure(text="Wirklich alles löschen?",
                                        fg_color=WARN, hover_color=WARN)
            def revert():
                if getattr(self, "_all_armed", False):
                    self._all_armed = False
                    self.total_button.configure(text="Alle löschen",
                                                fg_color=ACCENT,
                                                hover_color=ACCENT_D)
            self._all_armed_job = self.after(3200, revert)

    def _do_delete(self, target):
        # Einzig zentraler Busy-Guard: schützt ALLE Einstiege (Button, Tray-Karte,
        # Tray-Dialog) vor parallelen Workern (Delete neben Delete/Scan)
        if self._busy:
            return
        # H1-Fix, zweite Verteidigungslinie (die UI verbaut unsichere Karten
        # bereits): unsichere Pfade werden NIE gelöscht.
        if target.get("all"):
            if not any(c["safe"] for c in self.cards):
                self._set_status("Kein gültiger Temp-Pfad gefunden — "
                                 "Löschen verweigert.", WARN)
                return
        else:
            c = self.cards[target["idx"]]
            if not c["safe"]:
                self._set_status(f"Pfad unzulässig: {c['unsafe_reason']} — "
                                 "Löschen verweigert.", WARN)
                return
        self._cancel_rescan()
        self._set_busy(True)
        scope = "alle Temp-Ordner" if target.get("all") else "einen Ordner"
        self._set_status(f"Leere {scope} …", INK_SOFT)
        self.status_dot.configure(text_color=WARN)
        self.status_head.configure(text="Leere …")
        threading.Thread(target=self._delete_worker, args=(target,),
                         daemon=True).start()

    def _delete_worker(self, target):
        try:
            if target.get("all"):
                # jeden physischen Ordner nur einmal (Dedup), nur SICHERE Pfade
                seen, jobs = set(), []
                for c in self.cards:
                    if not c["safe"]:
                        continue
                    p = os.path.realpath(c["path"]) if c["path"] else None
                    if p and p not in seen:
                        seen.add(p)
                        jobs.append(p)
            else:
                c = self.cards[target["idx"]]
                p = os.path.realpath(c["path"]) if c["path"] else None
                jobs = [p] if (p and c["safe"]) else []
            freed = deleted = skipped = blocked = 0
            for p in jobs:
                f, d, s, b = delete_folder_contents(p)
                freed += f
                deleted += d
                skipped += s
                blocked += b
        except Exception:
            # Sicherheitsnetz (wie beim Scan-Worker): ohne Callback würde die UI
            # für immer "busy" bleiben. In der console-less EXE ist
            # print_exc() ein No-Op (sys.stderr ist None) -> Details ins Log.
            if sys.stderr is not None:
                traceback.print_exc()
            _log_error("delete_worker", traceback.format_exc())
            self._ui_queue.put(self._on_delete_error)
            return
        # thread-sicher: Ergebnis in Queue legen, Main-Thread führt _on_deleted aus
        self._ui_queue.put(
            lambda: self._on_deleted(freed, deleted, skipped, blocked))

    def _on_delete_error(self):
        """Unerwarteter Fehler im Delete-Worker: UI wieder freigeben (Main-Thread)."""
        if self._closing:
            return
        self._set_busy(False)
        self.status_head.configure(text="Fehler")
        self.status_dot.configure(text_color=WARN)
        self._status_mode = "result"   # Ticker lässt die Meldung stehen
        self._set_status(
            "Fehler beim Löschen — Details: "
            "%LOCALAPPDATA%\\Temp-Reiniger\\error.log", WARN)

    def _on_deleted(self, freed, deleted, skipped, blocked=0):
        if self._closing:
            return
        # Worker ist fertig -> UI WIEDER FREIGEBEN (auch während des 3-s
        # Result-Fensters bis zum Auto-Rescan; sonst: grüner OK-Punkt bei
        # deaktivierten Buttons)
        self._set_busy(False)
        self.status_head.configure(text="Fertig")
        self.total_button.configure(text="Alle löschen", fg_color=ACCENT,
                                    hover_color=ACCENT_D)
        # "Einträge" statt "Dateien": Link-Einträge (Symlinks/Junctions)
        # zählen hier ebenfalls mit.
        msg = (f"{format_bytes(freed)} entfernt · {format_count(deleted)} "
               f"{_plural_de(deleted, 'Eintrag', 'Einträge')}")
        self._status_mode = "result"
        # Amber, wenn Etwas geblieben ist: übersprungene Einträge ODER
        # Ordner, die nicht einmal eingelesen werden konnten (Rechte) —
        # in beiden Fällen ist die Löschung NICHT vollständig.
        if skipped or blocked:
            extra = []
            if skipped:
                extra.append(f"{format_count(skipped)} übersprungen")
            if blocked:
                extra.append(f"{format_count(blocked)} "
                             f"{_plural_de(blocked, 'Eintrag', 'Einträge')} "
                             f"nicht lesbar")
            self._set_status(msg + " · " + " · ".join(extra), WARN)
            self.status_dot.configure(text_color=WARN)
        else:
            self._set_status(msg, OK)
            self.status_dot.configure(text_color=OK)
        # Ordner automatisch neu einscannen — mit kurzer Verzögerung, damit die
        # freigemachte Größe (MB/GB) im Status sichtbar bleibt.
        self._schedule_rescan(3000)

    # ------------------------------------------------------------- Tray
    def _start_tray(self):
        """System-Tray-Icon in einem eigenen Thread starten (Windows).

        `_tray_active` wird hier optimistisch gesetzt; der 1-s-Health-Check
        (_tray_health, läuft im _status_ticker) degradiert bei nachweislich
        fehlendem Icon (Setup-Thread tot / Icon nicht sichtbar) auf
        "Close = Quit" mit Status-Hinweis.
        """
        try:
            import pystray
        except Exception:
            return
        def run():
            try:
                self._tray_icon = pystray.Icon(
                    "Temp-Reiniger", make_tray_icon(), "Temp-Reiniger",
                    self._build_menu(),
                )
                self._tray_ready = True
                self._tray_active = True
                self._tray_started = time.monotonic()
                self._tray_icon.run()
            except Exception:
                # Tray-Thread tot: (1) pystray-Setup-Thread entblocken — er
                # wartet sonst auf ein Ready-Signal, das nie kommt (Non-
                # Daemon-Thread -> würde den Prozess-Exit blockieren),
                # (2) Degradation im Main-Thread (Fenster sichtbar halten,
                # Close = Quit).
                self._tray_queue_unblock()
                self._ui_queue.put(self._on_tray_dead)
        threading.Thread(target=run, name="tray", daemon=True).start()

    def _tray_queue_unblock(self):
        """pystray-Setup-Thread entblocken, falls der Tray-Thread gestorben ist,
        bevor das Ready-Signal gesendet wurde. Privat-Attribut von pystray
        (Name-Mangling: __queue -> _Icon__queue) — defensive, Versions-
        Robustheit über try/except."""
        icon = self._tray_icon
        if icon is None:
            return
        try:
            q = getattr(icon, "_Icon__queue", None)
            if q is not None:
                q.put(True)
        except Exception:
            pass

    def _tray_health(self):
        """1-s-Check: nachweislich fehlendes Tray-Icon erkennen und
        degradieren (Close = Quit).

        pystray-Semantik: der Setup-Thread ist ONE-SHOT — er ENDET nach
        `visible = True` (Normalzustand!). Also:
          - Setup-Thread lebt  -> noch am Werk (kein Urteil),
          - Setup-Thread tot + visible=True  -> Erfolg (auch bei still
            fehlgeschlagenem NIM_ADD: sichtbar gemeldet, toleriert),
          - Setup-Thread tot + visible=False -> S ist ABGESTÜRBT, bevor
            das Icon sichtbar wurde (z. B. Exception im _show()) ->
            DEGRADATION (3-s-Anlaufgrace, einmaliger Status-Hinweis).
        """
        icon = self._tray_icon
        if icon is None or self._tray_started is None:
            return
        age = time.monotonic() - self._tray_started
        if age < 3.0:
            return
        try:
            st = getattr(icon, "_setup_thread", None)
            alive = st.is_alive() if st is not None else True
            visible = bool(getattr(icon, "visible", True))
        except Exception:
            return
        if (not alive) and (not visible):
            if self._tray_active:
                self._tray_active = False
            # M3-Fix: war das Fenster in den Tray ausgeblendet, MUSS es zurück
            # — sonst wäre die App ohne Icon unerreichbar (wie _on_tray_dead).
            try:
                if self.state() == "withdrawn":
                    self.deiconify()
                    self.lift()
            except tk.TclError:
                pass
            if not self._tray_degraded_hint:
                self._tray_degraded_hint = True
                self._status_mode = "result"   # Ticker nicht drüberschreiben
                self.status_dot.configure(text_color=WARN)
                self._set_status(
                    "Tray-Icon nicht verfügbar — Schließen beendet jetzt "
                    "die App.", WARN)

    def _on_tray_dead(self):
        """Tray-Thread ist tot (Exception in pystray): Degradation im
        Main-Thread — Close = Quit; war das Fenster ausgeblendet, wieder
        anzeigen (sonst wäre die App unerreichbar)."""
        if self._closing:
            return
        self._tray_active = False
        try:
            if self.state() == "withdrawn":
                self.deiconify()
                self.lift()
        except tk.TclError:
            pass
        if not self._tray_degraded_hint:
            self._tray_degraded_hint = True
            self._status_mode = "result"
            self.status_dot.configure(text_color=WARN)
            self._set_status(
                "Tray-Icon ausgefallen — App läuft weiter im Fenster "
                "(Schließen beendet jetzt die App).", WARN)

    def _build_menu(self):
        """Rechtsklick-Menü: die 4 Lösch-Optionen + Öffnen + Beenden.

        "Fenster öffnen" ist das Default-Item: Linksklick aufs Icon = Fenster
        öffnen. Destruktive Aktionen bleiben ausschließlich dem Menü
        (explizite Auswahl) vorbehalten.
        """
        import pystray
        defs = temp_definitions()
        labels = []
        for i, (token, _p) in enumerate(defs):
            labels.append(f"{token} leeren" +
                          ("" if self.cards[i]["safe"] else " (unzulässig)"))
        return pystray.Menu(
            pystray.MenuItem(labels[0],
                             lambda i, it: self._tray_action("card", 0)),
            pystray.MenuItem(labels[1],
                             lambda i, it: self._tray_action("card", 1)),
            pystray.MenuItem(labels[2],
                             lambda i, it: self._tray_action("card", 2)),
            pystray.MenuItem("Alle Temp-Ordner leeren",
                             lambda i, it: self._tray_action("all", None)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Fenster öffnen",
                             lambda i, it: self._tray_show(),
                             default=True),
            pystray.MenuItem("Temp-Reiniger beenden",
                             lambda i, it: self._tray_quit()),
        )

    def _tray_action(self, kind, idx):
        """Tray-Menü: Löschen ausführen (explizite Menüwahl).

        Läuft im Tray-Thread: nur Queue-Hand-off. Busy-/Unsicher-Checks und
        Feedback geschehen im Main-Thread — sonst stumme Drops ohne
        Feedback (L9-Fix).
        """
        if self._closing:
            return
        if kind == "all":
            # destruktiv: kurze Bestätigung im Main-Thread (siehe _confirm_tray_all)
            self._ui_queue.put(self._confirm_tray_all)
        else:
            self._ui_queue.put(lambda i=idx: self._on_tray_card(i))

    def _on_tray_card(self, idx):
        """Tray-Karten-Löschen im Main-Thread: mit Feedback statt stummer
        Drops."""
        if self._closing:
            return
        c = self.cards[idx]
        if not c["safe"]:
            self._set_status(f"Pfad unzulässig: {c['unsafe_reason']} — "
                             "Löschen verweigert.", WARN)
            return
        if self._busy:
            self._set_status("Etwas läuft gerade — Aktion verworfen.", WARN)
            return
        self._do_delete({"idx": idx})

    def _confirm_tray_all(self):
        """Tray 'Alle leeren': Bestätigung (läuft im Main-Thread)."""
        if self._closing:
            return
        if self._busy:
            # NIE stumm verwerfen: explizite Menüwahl braucht Feedback
            # (unabhängig vom aktuellen Status-Modus).
            self._set_status("Etwas läuft gerade — Aktion verworfen.", WARN)
            return
        if not any(c["safe"] for c in self.cards):
            self._set_status("Kein gültiger Temp-Pfad gefunden — "
                             "Löschen verweigert.", WARN)
            return
        # Modal-Text: bekannte Größe/Alter + ECHTE Anzahl eindeutiger
        # sicherer Ordner (Standard-Maschine: %TEMP% == %LOCALAPPDATA%\Temp
        # -> 2, nicht 3).
        uniq = len({os.path.realpath(c["path"])
                    for c in self.cards if c["safe"] and c["path"]})
        size = (format_bytes(self._last_total)
                if self._last_total is not None else "…")
        age = self._last_scan_str or "noch nicht eingelesen"
        if tk_messagebox.askyesno(
            "Alle Temp-Ordner leeren",
            f"Wirklich {uniq} Temp-Ordner leeren?\n"
            f"{size} · eingelesen {age}\n"
            "Gesperrte Dateien werden übersprungen.",
        ):
            # M1-Fix: TOCTOU nach dem Modal — der Auto-Rescan (+3 s) kann
            # während des offenen Dialogs _busy gesetzt haben; der stumme
            # Busy-Return in _do_delete würde ein explizites "Ja"
            # verschlucken (verletzt "Stille Tray-Drops gibt es nicht") ->
            # revalidieren + Feedback statt Silence.
            if self._closing:
                return
            if self._busy:
                self._set_status("Etwas läuft gerade — Aktion verworfen.",
                                 WARN)
                return
            self._do_delete({"all": True})

    def _tray_show(self):
        if self._closing:
            return
        self._ui_queue.put(self._show_window)

    def _tray_quit(self):
        if self._closing:
            return
        self._ui_queue.put(self._do_quit)

    def _show_window(self):
        if self._closing:
            return
        try:
            self.deiconify()
            self.state("normal")
            self.lift()
            self.focus_force()
        except tk.TclError:
            pass

    def _poll_ui(self):
        """Haupt-Thread-Poller: führt Main-Thread-Kommandos sicher im Tk-Thread aus.

        Tray-Aktionen UND Worker-Callbacks (Scan/Delete) laufen dadurch immer im
        Main-Thread -> thread-sichere Entkopplung (kein after(0, ...) aus Threads).
        """
        if self._closing:
            return
        if self._poll_active:
            # M2-Fix: Re-Entry-Schutz — Tk's Modal-Loop dispatcht after()-Timer
            # AUCH während eines offenen askyesno. Ohne Flag würde der Poller
            # sich unter dem Dialog selbst reentravieren: wartende Kommandos
            # (destruktive Deletes!) liefen UNTER dem unbeantworteten Dialog,
            # und jeder Modal forkt dauerhaft eine extra Poller-Kette.
            return
        self._poll_active = True
        try:
            while True:
                fn = self._ui_queue.get_nowait()
                try:
                    fn()
                except Exception:
                    # EIN fehlerhaftes Kommando darf den Poller nicht töten:
                    # sonst wären Tray-Aktionen + UI-Updates für immer tot
                    # (App nicht mehr beendigbar). Fehler loggen, weiterpollen.
                    # (In der windowed EXE ist sys.stderr None -> print_exc()
                    # ist ein No-Op; das Log-File ist der verlässliche Ort.)
                    if sys.stderr is not None:
                        traceback.print_exc()
                    _log_error("ui_poll", traceback.format_exc())
        except queue.Empty:
            pass
        finally:
            self._poll_active = False
        if self._closing:
            return
        self._poll_job = self.after(120, self._poll_ui)

    def _on_unmap(self, event):
        """Minimieren -> in den Tray verschwinden (Fenster ausblenden)."""
        # Tooltip (eigenes overrideredirect-Toplevel) nicht im Desktop
        # schweben lassen, wenn das Hauptfenster ausgeblendet wird
        for c in self.cards:
            tip = c.get("tooltip")
            if tip is not None:
                tip.hide()
        if self._closing or not getattr(self, "_tray_active", False):
            return
        try:
            if self.state() == "iconic":
                self.withdraw()
        except tk.TclError:
            pass

    def _do_quit(self):
        if self._closing:
            return
        self._closing = True
        self._cancel_rescan()
        # D4-Fix: auch Ticker/Poller/Tween-Timer canceln — sonst feuern sie
        # nach destroy() als gelöschte Tcl-Kommandos (Hintergrundfehler-Noise,
        # den der Arm-Job-Kommentar unten genau vermeiden will).
        for _job in (self._ticker_job, self._poll_job,
                     *self._tween_jobs.values()):
            if _job is None:
                continue
            try:
                self.after_cancel(_job)
            except Exception:
                pass
        if self._busy:
            # DESIGN: Beenden während Delete = Abbruch, erneuter Lauf vollendet.
            # Der abgebrochene Lauf war bisher komplett ungeloggt.
            _log_error("quit", "Beenden während eines laufenden Workers — "
                               "Lösch-/Scan-Lauf evtl. unvollständig beendet.")
        # Arm-Jobs (Zwei-Stufen-Bestätigung) abbrechen: sonst feuert ein
        # verbliebener after()-Revert NACH dem destroy und configure() auf
        # einem zerstörten Widget -> TclError-Noise via report_callback_exception
        for c in self.cards:
            if c["armed_job"]:
                try:
                    self.after_cancel(c["armed_job"])
                except Exception:
                    pass
                c["armed_job"] = None
                c["armed"] = False
        if getattr(self, "_all_armed_job", None):
            try:
                self.after_cancel(self._all_armed_job)
            except Exception:
                pass
            self._all_armed_job = None
        self._all_armed = False
        icon = getattr(self, "_tray_icon", None)
        if icon is not None:
            try:
                icon.stop()
            except Exception:
                pass
        self.destroy()

    # ------------------------------------------------------------- close
    def _on_close(self):
        # Fenster schließen -> in Tray minimieren (Beenden über Tray-Menü)
        if self._closing:
            return
        if getattr(self, "_tray_active", False):
            self.withdraw()
        else:
            self._do_quit()


def _dev_screenshot(app, out_path, mock):
    """Fenster rendern, Größen setzen (echtes Einlesen oder Mock), speichern."""
    from PIL import ImageGrab  # Lazy: nur im Dev-Modus nötig

    if mock:
        # synthetische Demo-Werte (nur fürs Layout-Bild, NICHT echt)
        demo = {0: (2_340_000_000, 1244, 0), 1: (812_000_000, 389, 0),
                2: (456_000_000, 207, 0)}
        app._on_scanned([(k, demo[k]) for k in demo])
    else:
        # echtes Einlesen (Nur lesen) bis fertig
        for _ in range(600):
            if not app._busy:
                break
            app.update()
            time.sleep(0.1)

    app.update_idletasks()
    app.update()
    time.sleep(0.5)
    app.update()
    # Füllstand/Animationen kurz einlaufen lassen
    for _ in range(40):
        app.update()
        time.sleep(0.02)
    x, y = app.winfo_rootx(), app.winfo_rooty()
    w, h = app.winfo_width(), app.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    img.save(out_path)
    print(f"[dev] Screenshot gespeichert: {out_path}")


_INSTANCE_MUTEX = None


def _acquire_instance_mutex():
    """Single-Instance-Schutz: benannter Mutex (CreateMutexW).

    Zwei Instanzen könnten denselben Temp-Ordner parallel leeren (Doppel-
    Zählung der "entfernten" Größe + Races um dieselben Dateien).
    ERROR_ALREADY_EXISTS (183) => eine Instanz läuft bereits.
    L1-Fix: FAIL-CLOSED — ein NULL-Handle (z. B. ERROR_ACCESS_DENIED an einem
    fremd vorerzeugten Mutex-Objekt) LEHNT ab statt zu starten; sonst erzwingt
    ein Angreifer genau die Doppel-Instanz, vor der der Mutex schützt.
    GetLastError über das thread-lokale use_last_error (ctypes-Regel: rohes
    kernel32.GetLastError() ist nicht sicher, Python kann dazwischen WinAPI
    aufrufen).
    """
    global _INSTANCE_MUTEX
    import ctypes.wintypes as wt
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateMutexW.restype = wt.HANDLE   # ohne restype: 64-Bit-Handles truncate
    h = k32.CreateMutexW(None, False, "Local\\Temp-Reiniger")
    err = ctypes.get_last_error()
    if not h or err == 183:
        return False
    _INSTANCE_MUTEX = h   # bis zum Prozess-Ende halten (Kernel räumt auf)
    return True


def main():
    if getattr(sys, "frozen", False):
        # M5-Fix: Die taeuschenden Dev-Modi NUR aus dem Quellcode. Nie in
        # der ausgelieferten EXE — sonst zeigt MOCK+SCREENSHOT fake Größen
        # VOR echten Deletes (und ein schiefer Screenshot-Pfad hielt die
        # luegende UI offen). LAUNCH_CHECK bleibt erlaubt: reiner
        # Build-Smoke-Test (UI + Tray aufbauen, sauber beenden, NICHTS
        # loescht) — genau der Weg, mit dem gebaute EXEn verifiziert werden.
        for _k in ("TEMP_REINIGER_MOCK", "TEMP_REINIGER_SCREENSHOT"):
            os.environ.pop(_k, None)
    mock = os.environ.get("TEMP_REINIGER_MOCK") == "1"
    shot = os.environ.get("TEMP_REINIGER_SCREENSHOT")
    launch_check = os.environ.get("TEMP_REINIGER_LAUNCH_CHECK")
    if not _acquire_instance_mutex():
        tk_messagebox.showinfo(
            "Temp-Reiniger",
            "Temp-Reiniger läuft bereits — oder der Instanz-Schutz war nicht "
            "verfügbar (Single-Instance-Modus).")
        sys.exit(0)
    # MOCK-Modus: Start-Scan unterdrücken (reines Layout-Bild; sonst würde
    # das echte Einlesen die Demo-Werte überlaufen lassen)
    app = TempApp(initial_scan=not mock)
    if launch_check:
        # Nur: UI + Tray-Icon aufbauen, kurz warten, sauber beenden (kein Löschen).
        def check():
            tray_ok = False
            for _ in range(40):  # bis ~2 s auf das Tray-Icon warten
                try:
                    app.update()
                except tk.TclError:
                    break
                time.sleep(0.05)
                tray_ok = getattr(app, "_tray_ready", False)
                if tray_ok:
                    break
            app._do_quit()
            label = "OK" if tray_ok else "NO-TRAY"
            try:
                with open(os.path.join(os.getcwd(), "launch_check.txt"), "w",
                          encoding="utf-8") as f:
                    f.write(label)
            except Exception:
                pass
            print("[dev] LAUNCH-" + label)
        app.after(2500, check)
    elif shot:
        def run_capture():
            try:
                _dev_screenshot(app, shot, mock)
            finally:
                # M5-Fix: auch bei fehlerhaftem Screenshot (ImageGrab/save)
                # MUSS beendet werden — sonst blieb eine MOCK-UI mit Fake-
                # Größen stehen. Sauber über _do_quit (setzt _closing, stoppt
                # das Tray-Icon, bricht Arm-Jobs ab) — nicht roh destroy().
                app.after(250, app._do_quit)
        app.after(400 if mock else 2600, run_capture)
    app.mainloop()


if __name__ == "__main__":
    # Unbehandelte Exceptions propagieren: im PyInstaller-EXE-Modus
    # (console=False, disable_windowed_traceback=False) zeigt der Bootloader
    # dann ein native Fehlerdialog statt still zu sterben.
    main()