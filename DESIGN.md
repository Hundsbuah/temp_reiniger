# DESIGN — Temp-Reiniger (gebaut)

Dokumentiert die reale, gebaute Welt der App (`temp_reiniger.py`,
CustomTkinter, Windows, Single-EXE). Mode: **Operate**.

## Direction: „The Scale"
Drei Temp-Ordnere als drei **Instrument-Felder**. Nicht die graue
WinForms-Liste mit roten Buttons, nicht das Neon-Dashboard. Die drei
Ordner lesen sich wie drei Messfelder, die man leert.

## Palette (eigene Welt — mit Inhalt entfernt noch erkennbar)
| Rolle | Hex | Einsatz |
|---|---|---|
| Slate (Fenster) | `#E9EDF3` | Hintergrund, kühles helles Slate (nicht Creme) |
| Card | `#FFFFFF` | Kartenfläche, matte weiße Platte |
| Card-Line | `#D9E0EA` | 1px Karten-Border + 14px Radius (gehobene Platte) |
| Ink | `#141A24` | Haupttext + große Zahlen |
| Ink-Soft | `#5E6B7D` | Eyebrows, Zähler, Status |
| Ink-Faint | `#93A0B0` | Pfade (mono) |
| Accent (Teal) | `#1296B0` | Füllstand + Buttons, kein Glow |
| Accent-D | `#0C7285` | Button-Hover |
| Track | `#DCE6EC` | Füllstand-Schiene |
| OK (Grün) | `#2E9E5B` | Status-Punkt, „entfernt" |
| Warn (Amber) | `#C9701E` | Zwei-Stufen-Bestätigung, „übersprungen" |

Strategie: **Restrained** — Neutrals + ein Akzent. Hell, weil *Reinigen*
klar/frisch bedeutet; bewusst Abstand zu den AI-Defaults (Creme+Serif,
Near-Black+Neon+Glow, Broadsheet-Haarlinien).

## Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling)
| Rolle | Schrift | Größe | Warum |
|---|---|---|---|
| Große Zahlen / Gesamt | **Bahnschrift** (bold) | 30 / 44 | industrial, „Instrument-Readout" |
| Kartentitel (Env-Token) | **Bahnschrift** (bold) | 16 | technische Kopfzeile |
| Wortmarke | **Bahnschrift** (bold) | 15 | Markenzeichen oben links |
| Pfad | **Consolas** | 11 | Daten / mono, Tooltip zeigt vollen Pfad |
| Text / Labels / Buttons | **Segoe UI** | 11–13 | Workhorse, native Lesbarkeit |

## Layout / Komposition
Kopfzeile (Wortmarke links `● TEMP-REINIGER`; rechts Ghost-Button
`Aktualisieren` (Refresh) + Status `● Bereit · C:\ · 3 Temp-Ordner`) →
**drei gleiche Karten nebeneinander** → Gesamt-Zeile über alle drei →
Fußstatusleiste.

Karte (innen, Grid, dehnbarer Zwischenraum vor dem Button):
```
%TEMP%                 Titel (Bahnschrift)
E:\WindowsTemp         Pfad (mono, Tooltip = voller Pfad)
2,18 GB                große Zahl (Kopfzeile)
██████████▌            Füllstand (relativ zum größten Ordner)
1 244 Dateien          Zähler
                       [Temp löschen]   Button (Fußzeile)
```
Gesamt-Zeile: links Eyebrow `GESAMT · ALLE TEMP-ORDNER` + größte Zahl
(44px) + optionaler Duplikat-Hinweis; rechts Button `Alle löschen`.

## Signature (das Memorale)
**Relative Füllstand-Leiste + große Bahnschrift-Zahl.** Man sieht sofort,
welcher Ordner am schwersten ist (größter = volle Leiste). Nach dem Leeren
sinken Zahl und Leiste (Tween vom alten zum neuen Wert) — das „Leerziehen".

## Motion-Grammatik
- Scan fertig → Zahlen zählen hoch (ease-out, ~0,5 s), Leisten füllen sich
  (leicht gestaffelt). Ein georchestrierter Moment, nicht verstreut.
- Nach Löschen → Zahl/Leiste sinken von alt zu neu (gleicher Tween).
- Button-Hover + Zwei-Stufen-Armierung (Farbe → Amber, Text „Wirklich …?").

## Zustände
- **Aktualisieren (Refresh):** Ghost-Button in der Kopfzeile rechts; re-liest
  die drei Ordner (reiner Refresh, **kein Löschen**). Während Scan:
  deaktiviert + Text „Aktualisiere …
- **Scannen:** Status „Wird eingelesen …", Zahlen `…`, Punkte amber.
- **Bereit:** `● Bereit · eingelesen HH:MM · X gesamt`.
- **Löschen (armiert):** Button amber, „Wirklich löschen?" / „Wirklich alles löschen?".
- **Entfernt:** Status grün `X entfernt · N Dateien`.
- **Übersprungen:** Status amber `… · K übersprungen` (gesperrte Dateien).
- **Duplikat:** Hinweis `zwei Pfade zeigen auf denselben Ordner`.
- **Leerer Ordner:** `0 B`, Leiste leer (kein Fehlerzustand).

## Sicherheitsregeln (gebaut)
- Beim Start wird **nie** gelöscht — nur eingelesen.
- Löschen nur per explizitem Button (zwei Schritte).
- Wurzelmappen bleiben immer — nur der Inhalt wird entfernt.
- Gesperrte/in-Benutzung Dateien werden übersprungen, kein Abbruch.
- `C:\Windows\Temp` ohne Admin nur teilweise leerbar (Überspringen).
- UI bleibt reaktionsschnell (Worker-Thread + `after`-Marshalling).