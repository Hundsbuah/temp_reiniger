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
  Kopfzeile (Wortmarke links, Status-Punkt rechts). Darunter drei gleiche
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
  - Löschen erfolgt nur durch expliziten Button-Klick (zwei Schritte).
  - Wurzelmappen selbst werden NIE gelöscht — nur deren Inhalt.
  - Gesperrte Dateien werden übersprungen (kein Abbruch).
"""

import os
import time
import threading
import traceback
import tkinter as tk
import customtkinter as ctk

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
    """Byte-Größe als lesbare Zeichenfolge (deutsche Konvention)."""
    if n is None:
        return "…"
    if n < 0:
        n = 0
    if n < 1000:
        return f"{int(n)} B"
    units = ["KB", "MB", "GB", "TB", "PB"]
    v = float(n)
    i = -1
    while v >= 1024 and i < len(units) - 1:
        v /= 1024.0
        i += 1
    return f"{_de(v, 2)} {units[i]}"


def format_count(n):
    if n is None:
        return "…"
    return f"{int(n):,}".replace(",", THIN_SPACE)


# --------------------------------------------------------------------------- #
#  Datei-Logik (nur lesen / löschen von INHALT, nie die Wurzel)
# --------------------------------------------------------------------------- #
def scan_folder(path):
    """(gesamte Gröe in Byte, Dateianzahl) eines Ordners zählen.

    Fehler (z. B. fehlende Rechte beim Einlesen) werden still ignoriert.
    """
    total, count = 0, 0
    if not path or not os.path.isdir(path):
        return 0, 0
    for dirpath, _dirnames, filenames in os.walk(path, onerror=lambda e: None):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            try:
                st = os.lstat(fp)
                total += st.st_size
                count += 1
            except OSError:
                pass
    return total, count


def delete_folder_contents(top):
    """Nur den INHALT von `top` löschen. `top` selbst bleibt bestehen.

    Rückgabe: (freier Byte, gelöschte Dateien, übersprungene Einträge).
    Sperrungen (in Benutzung / keine Rechte) werden übersprungen.
    """
    top = os.path.abspath(top)
    freed = deleted = skipped = 0
    if not os.path.isdir(top):
        return 0, 0, 0
    for dirpath, _dirnames, filenames in os.walk(top, topdown=False):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            try:
                st = os.lstat(fp)
                os.remove(fp)
                freed += st.st_size
                deleted += 1
            except (PermissionError, OSError):
                skipped += 1
        if dirpath != top:
            try:
                os.rmdir(dirpath)          # nur, wenn leer; Wurzel bleibt
            except OSError:
                pass
    return freed, deleted, skipped


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
        if self.tip:
            self.tip.destroy()
            self.tip = None


# --------------------------------------------------------------------------- #
#  Anwendung
# --------------------------------------------------------------------------- #
class TempApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._closing = False
        self._busy = False
        self._tween_tokens = {}
        self._all_armed = False
        self._all_armed_job = None
        self._prev_total = 0

        ctk.set_appearance_mode("Light")
        self.title("Temp-Reiniger")
        self._center(self, 1060, 600)
        self.minsize(920, 540)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

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
        self._scan_all()   # beim Start nur einlesen — niemals löschen

    # ------------------------------------------------------------- layout
    def _center(self, win, w, h):
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2 - 40)
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
        self.status_dot = ctk.CTkLabel(right, text=DOT, font=self.f_small,
                                       text_color=OK)
        self.status_dot.pack(side="left", padx=(0, 7))
        self.status_head = ctk.CTkLabel(right, text="Bereit", font=self.f_body,
                                        text_color=INK_SOFT)
        self.status_head.pack(side="left")
        ctk.CTkLabel(right, text=f"C:\\ · {len(temp_definitions())} Temp-Ordner",
                     font=self.f_small, text_color=INK_FAINT
                     ).pack(side="left", padx=(14, 0))

    def _build_card(self, root, idx, title, path):
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
        shown = self._ellipsize(full, 30)
        path_lbl = ctk.CTkLabel(card, text=shown, font=self.f_path,
                                text_color=INK_FAINT, anchor="w")
        path_lbl.grid(row=1, column=0, sticky="ew", padx=20, pady=(2, 0))
        Tooltip(path_lbl, full)

        # Große Zahl
        num = ctk.CTkLabel(card, text="…", font=self.f_num, text_color=INK,
                           anchor="w")
        num.grid(row=2, column=0, sticky="ew", padx=20, pady=(16, 2))
        # Füllstand-Leiste
        bar = ctk.CTkProgressBar(card, fg_color=TRACK, progress_color=ACCENT,
                                 height=9, corner_radius=5)
        bar.set(0.0)
        bar.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 8))
        # Dateizahl
        count = ctk.CTkLabel(card, text="—", font=self.f_body,
                             text_color=INK_SOFT, anchor="w")
        count.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 2))

        # Lösch-Button
        btn = ctk.CTkButton(
            card, text="Temp löschen", font=self.f_btn, height=42,
            fg_color=ACCENT, hover_color=ACCENT_D, text_color="#FFFFFF",
            corner_radius=9, command=lambda i=idx: self._on_card_delete(i),
        )
        btn.grid(row=6, column=0, sticky="ew", padx=20, pady=(10, 20))

        self.cards.append({
            "idx": idx, "title": title, "path": path,
            "num": num, "bar": bar, "count": count, "button": btn,
            "armed": False, "armed_job": None, "bytes": None, "nfiles": None,
        })

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

    def _set_busy(self, busy):
        self._busy = busy
        state = "disabled" if busy else "normal"
        for c in self.cards:
            c["button"].configure(state=state)
        self.total_button.configure(state=state)
        if busy:
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
        def step(i):
            if self._closing:
                return
            if self._tween_tokens.get(key) != token:
                return
            t = min(1.0, i / steps)
            e = 1 - (1 - t) ** 3            # ease-out
            apply(from_v + (to_v - from_v) * e)
            if i < steps:
                self.after(16, lambda: step(i + 1))
            else:
                apply(to_v)
                if done:
                    done()
        step(0)

    # ------------------------------------------------------------- Scan
    def _scan_all(self):
        self._set_busy(True)
        self._set_status("Wird eingelesen …", INK_SOFT)
        self.status_dot.configure(text_color=WARN)
        for c in self.cards:
            c["num"].configure(text="…")
            c["count"].configure(text="—")
            c["bar"].set(0.0)
        self.total_num.configure(text="…")
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        memo = {}
        for c in self.cards:
            p = c["path"]
            if p not in memo:
                try:
                    memo[p] = scan_folder(p)
                except Exception:
                    memo[p] = (0, 0)
        payload = [(c["idx"], memo.get(c["path"], (0, 0))) for c in self.cards]
        try:
            self.after(0, lambda: self._on_scanned(payload))
        except tk.TclError:
            pass

    def _on_scanned(self, payload):
        if self._closing:
            return
        for idx, (b, n) in payload:
            c = self.cards[idx]
            c["bytes"], c["nfiles"] = b, n
        # relative Füllstand (gröster Ordner = voll)
        max_b = max((c["bytes"] or 0) for c in self.cards) or 1
        total = sum(c["bytes"] or 0 for c in self.cards)
        # Duplikat-Hinweis (gleicher physischer Pfad)
        paths = [os.path.realpath(c["path"]) if c["path"] else None for c in self.cards]
        dup = len(set(paths)) < len(paths)
        self.total_note.configure(
            text=("Hinweis: zwei Pfade zeigen auf denselben Ordner "
                  "(wird doppelt angezeigt).") if dup else ""
        )
        for i, c in enumerate(self.cards):
            frac = (c["bytes"] or 0) / max_b
            prev_bar = c.get("prev_bar") or 0.0
            prev_b = c.get("prev_bytes") or 0
            self._tween(f"bar{i}", prev_bar, frac, c["bar"].set, 520 + i * 70)
            self._tween(f"num{i}", float(prev_b), float(c["bytes"] or 0),
                        lambda v, n=c["num"]: n.configure(text=format_bytes(int(v))),
                        520 + i * 70)
            c["count"].configure(text=f"{format_count(c['nfiles'])} Dateien")
            c["prev_bar"] = frac
            c["prev_bytes"] = c["bytes"]
        self._tween("total", float(self._prev_total), float(total),
                    lambda v: self.total_num.configure(text=format_bytes(int(v))),
                    560)
        self._prev_total = total
        # fertig
        self._set_busy(False)
        self.status_dot.configure(text_color=OK)
        now = time.strftime("%H:%M")
        self._set_status(f"Bereit · eingelesen {now} · {format_bytes(total)} gesamt",
                         INK_SOFT)

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
        self._set_busy(True)
        scope = "alle Temp-Ordner" if target.get("all") else "einen Ordner"
        self._set_status(f"Leere {scope} …", INK_SOFT)
        self.status_dot.configure(text_color=WARN)
        threading.Thread(target=self._delete_worker, args=(target,),
                         daemon=True).start()

    def _delete_worker(self, target):
        if target.get("all"):
            # jeden physischen Ordner nur einmal (Dedup)
            seen, jobs = set(), []
            for c in self.cards:
                p = os.path.realpath(c["path"]) if c["path"] else None
                if p and p not in seen:
                    seen.add(p)
                    jobs.append(p)
        else:
            c = self.cards[target["idx"]]
            p = os.path.realpath(c["path"]) if c["path"] else None
            jobs = [p] if p else []
        freed = deleted = skipped = 0
        for p in jobs:
            f, d, s = delete_folder_contents(p)
            freed += f
            deleted += d
            skipped += s
        try:
            self.after(0, lambda: self._on_deleted(freed, deleted, skipped))
        except tk.TclError:
            pass

    def _on_deleted(self, freed, deleted, skipped):
        if self._closing:
            return
        self.total_button.configure(text="Alle löschen", fg_color=ACCENT,
                                    hover_color=ACCENT_D)
        msg = (f"{format_bytes(freed)} entfernt · {format_count(deleted)} "
               f"Dateien")
        if skipped:
            self._set_status(msg + f" · {format_count(skipped)} übersprungen",
                             OK if skipped == 0 else WARN)
        else:
            self._set_status(msg, OK)
        self.status_dot.configure(text_color=OK)
        # frische Größe holen (nur lesen)
        self._scan_all()

    # ------------------------------------------------------------- close
    def _on_close(self):
        self._closing = True
        self.destroy()


def _dev_screenshot(app, out_path, mock):
    """Fenster rendern, Größen setzen (echtes Einlesen oder Mock), speichern."""
    from PIL import ImageGrab  # Lazy: nur im Dev-Modus nötig

    if mock:
        # synthetische Demo-Werte (nur fürs Layout-Bild, NICHT echt)
        demo = {0: (2_340_000_000, 1244), 1: (812_000_000, 389),
                2: (456_000_000, 207)}
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


def main():
    mock = os.environ.get("TEMP_REINIGER_MOCK") == "1"
    shot = os.environ.get("TEMP_REINIGER_SCREENSHOT")
    launch_check = os.environ.get("TEMP_REINIGER_LAUNCH_CHECK")
    app = TempApp()
    if launch_check:
        # Nur: UI aufbauen, Events kurz abarbeiten, sauber beenden (kein Löschen).
        def check():
            ok = True
            for _ in range(15):
                try:
                    app.update()
                except tk.TclError:
                    ok = False
                    break
                time.sleep(0.05)
            app.destroy()
            try:
                with open(os.path.join(os.getcwd(), "launch_check.txt"), "w",
                          encoding="utf-8") as f:
                    f.write("OK" if ok else "TCL-ERROR")
            except Exception:
                pass
            print("[dev] LAUNCH-OK" if ok else "[dev] LAUNCH-TCL-ERROR")
        app.after(2500, check)
    elif shot:
        def run_capture():
            _dev_screenshot(app, shot, mock)
            app.after(250, app.destroy)
        app.after(400 if mock else 2600, run_capture)
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise