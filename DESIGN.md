# DESIGN — Temp-Reiniger (gebaut)

Dokumentiert die reale, gebaute Welt der App (`temp_reiniger.py`,
CustomTkinter, Windows, Single-EXE). Mode: **Operate**.

## Direction: „The Scale"
Drei Temp-Ordner als drei **Instrument-Felder**. Nicht die graue
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
- **Bereit:** `● Bereit · eingelesen HH:MM · vor X Sekunden · X gesamt`
  (das „vor X Sekunden" zählt live hoch, 1-s-Ticker).
- **Löschen (armiert):** Button amber, „Wirklich löschen?" / „Wirklich alles löschen?".
- **Entfernt:** Status grün `X entfernt · N Einträge` (Link-Einträge zählen mit);
  bleibt ~3 s sichtbar, dann **automatischer Re-Scan** der Ordner (Größen fallen
  auf den Rest).
- **Übersprungen:** Status amber `… · K übersprungen` (gesperrte Dateien);
  zusätzlich `… · M Einträge nicht lesbar` (Ordner ohne Leserecht). Ein
  blockierte Ebene zählt einmal; schlägt das Entfernen dort fehl, werden ihre
  Eltern-Ebenen kaskadiert unterdrückt (keine Doppelzählung über die
  Ahnen-Kette). Feindliche Ordnernamen (z. B. `.`/`..`-Trick) werden per
  `\\?\`-Pfad-Rohpfad nachlesbar/nachlöschbar — gerettete Ordner zählen dann
  **nicht** mehr als „nicht lesbar".
- **Duplikat:** Hinweis `zwei Pfade zeigen auf denselben Ordner`.
- **Leerer Ordner:** `0 B`, Leiste leer (kein Fehlerzustand).

## System-Tray (Minimieren / Klicks)
- **Minimieren oder Schließen** des Fensters → Fenster wird ausgeblendet, die
  App lebt weiter als **Tray-Icon** (Teal-Platte mit weißem Papierkorb) —
  SOFERN das Tray-Icon verfügbar ist. Ein 1-s-Health-Check (Setup-Thread tot
  oder Icon nach 3 s Grace nicht sichtbar) erkennt das und **degradiert**:
  Close = Quit, einmaliger Status-Hinweis — und ein verstecktes (withdrawn)
  Fenster wird zurückgeholt, damit die App auch degradiert erreichbar bleibt.
- Grenze (Upstream, pystray 0.19.x): Nach einem **Explorer-Neustart**
  verschwindet das Tray-Icon, ohne dass `visible` oder der Icon-Queue das
  melden — pystray registriert sich nicht für die `TaskbarCreated`-Broadcast
  neu. Dieser Fall ist von außen nicht beobachtbar und degradiert daher nicht
  selbst; ein Neustart von außen scheitert am Instanz-Mutex. Behelf: Prozess
  beenden (Task-Manager) und neu starten.
- **Linksklick** aufs Icon: `Fenster öffnen` ist das Default-Item → Linksklick
  zeigt das Hauptfenster. Destruktive Aktionen bleiben dem Menü (explizite
  Auswahl) vorbehalten.
- **Rechtsklick** im Tray: die 4 Lösch-Optionen (`%TEMP% leeren`,
  `%LOCALAPPDATA%\Temp leeren`, `%SystemRoot%\Temp leeren`,
  `Alle Temp-Ordner leeren`) + `Fenster öffnen` + `Temp-Reiniger beenden`.
- Tray-Aktionen laufen über einen thread-sicheren Queue-Poller sicher in den
  Tk-Haupt-Thread (pystray hat einen eigenen Tray-Thread).
- Stille Tray-Drops gibt es nicht: Busy-Drops und „Alle leeren" aus dem Tray
  geben immer Status-Feedback („Etwas läuft gerade — Aktion verworfen.");
  der Bestätigungs-Dialog nennt Größe, Einlesezeitpunkt und die ECHTE Anzahl
  eindeutiger Ordner. Auch ein explizites „Ja" wird nach dem Schließen des
  Dialogs erneut gegen Busy-/Close-Zustand validiert (der Auto-Rescan kann
  während des offenen Dialogs gestartet sein) — Feedback statt verschlucktem
  Ja oder stillem Start.

## Sicherheitsregeln (gebaut)
- Beim Start wird **nie** gelöscht — nur eingelesen.
- Löschen nur per expliziter Auswahl: Button (zwei Schritte) oder Tray-Menü.
- JEDER Temp-Pfad wird validiert (absolut, kein Laufwerksroot/UNC, letzte
  Komponente endet auf „temp") — unzulässige Karten werden weder gescannt
  noch gelöscht und sind in der UI markiert (Button abgewertet, Tooltip
  begründet).
- Single-Instance: zweite Instanz wird abgelehnt (benannter Mutex,
  fail-CLOSED — ist der Mutex nicht erzeugbar, wird ebenfalls abgelehnt statt
  stillschweigend doppelt zu laufen).
- Dev-Modi (MOCK/SCREENSHOT) gibt es nur im Quellcode; die gebaute EXE
  ignoriert sie (keine vorgetäuschten Größen vor echten Deletes).
  LAUNCH_CHECK ist zerstörungsfrei (UI + Tray aufbauen, nichts löschen) und
  bleibt erlaubt — er verifiziert gebaute EXEs.
- Wurzelmappen bleiben immer — nur der Inhalt wird entfernt.
- Gesperrte/in-Benutzung Dateien werden übersprungen, kein Abbruch; nicht
  lesbare Ordner werden als „nicht lesbar" gezählt (Status amber).
- `C:\Windows\Temp` ohne Admin nur teilweise leerbar (Überspringen).
- Nach dem Löschen werden die Ordner **automatisch neu gescannt** (nach ~3 s,
  damit die freigemachte Größe sichtbar bleibt).
- Beenden während eines laufenden Deletes bricht es ab und protokolliert den
  Fall in `error.log`; ein erneuter Lauf vollendet die Löschung (idempotent).
- Unerwartete Fehler landen zusätzlich in `%LOCALAPPDATA%\Temp-Reiniger\error.log`.
- UI bleibt reaktionsschnell (Worker-Thread + `after`-Marshalling); Scan- UND
  Delete-Worker haben ein Exception-Netz mit garantiertem
  Completion-Callback (UI bleibt nie „busy" hängen).