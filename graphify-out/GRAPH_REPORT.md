# Graph Report - temp_delete  (2026-10-05)

## Corpus Check
- 12 files · ~8,546 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 172 nodes · 287 edges · 15 communities (9 shown, 6 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.86)
- Token cost: 142,540 input · 0 output

## Community Hubs (Navigation)
- Tk-Event-Handler & Module
- Win32-CTypes-Strukturen & E2E-Test
- Design-System & Design-Doku
- Loesch-Logik & Worker
- Screenshot: Karten & Status
- TempApp-Kern & Armierung
- Screenshot: Aktionen & Layout
- App-Start, Poller & Tray-Thread
- Tooltip-Komponente
- Tray-Menue & Aktionen
- UI-Aufbau & Temp-Definitionen
- Produkt-Dokumentation
- Delete-Flow & Bestaetigung
- Tray-Icon-Semantik
- Tray-Icon-Datei

## God Nodes (most connected - your core abstractions)
1. `TempApp` - 39 edges
2. `DESIGN.md — Temp-Reiniger Design-System` - 15 edges
3. `README.md — Temp-Reiniger (Produkt-Dokumentation)` - 14 edges
4. `format_bytes()` - 6 edges
5. `Tooltip` - 6 edges
6. `Temp-Reiniger Desktop UI (Screenshot)` - 6 edges
7. `%TEMP% Temp-Folder Card (E:\Windows\Temp)` - 6 edges
8. `%LOCALAPPDATA%\Temp Card (C:\Users\hundsbuah\AppData\Local\Temp)` - 6 edges
9. `%SystemRoot%\Temp Card (C:\WINDOWS\Temp)` - 6 edges
10. `Gesamt – Alle Temp-Ordner Summary (3,36 GB)` - 6 edges

## Surprising Connections (you probably didn't know these)
- `main()` --indirect_call--> `check()`  [INFERRED]
  temp_reiniger.py → _review_test.py
- `DESIGN.md — Temp-Reiniger Design-System` --references--> `Temp-Reiniger (temp_reiniger.py, CustomTkinter, Windows, Single-EXE)`  [EXTRACTED]
  DESIGN.md → README.md
- `README.md — Temp-Reiniger (Produkt-Dokumentation)` --references--> `Auto-Re-Scan nach dem Löschen (~3 s)`  [INFERRED]
  README.md → DESIGN.md
- `README.md — Temp-Reiniger (Produkt-Dokumentation)` --references--> `Sicherheitsregeln (gebaut)`  [INFERRED]
  README.md → DESIGN.md
- `README.md — Temp-Reiniger (Produkt-Dokumentation)` --references--> `Signatur: relative Füllstand-Leiste + große Bahnschrift-Zahl`  [INFERRED]
  README.md → DESIGN.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Temp-Reiniger Product Specification** — product, product_temp_reiniger, product_temp_folders, product_constraints, product_chosen_direction [INFERRED 0.80]
- **Sicherheits- und Responsiveness-Konzept (keine Wurzelmappen-Gefahr, explizite Auswahl, reaktive UI)** — design_safety_rules, design_two_step_confirmation, design_auto_rescan, design_worker_thread_marshalling [INFERRED 0.85]
- **System-Tray-Subsystem (pystray-Thread + Queue-Poller + Tray-UI)** — design_system_tray, design_tray_queue_poller, requirements_pystray [INFERRED 0.85]
- **Single-EXE-Verteilung (PyInstaller-Build → GitHub-Release → Download ohne Python)** — readme_pyinstaller_build, requirements_pyinstaller, readme_install_exe [INFERRED 0.85]
- **Temp-Folder Card Grid (3 Standard Windows Temp Locations)** — _impeccable_review_desktop_card_temp, _impeccable_review_desktop_card_localappdata_temp, _impeccable_review_desktop_card_systemroot_temp [INFERRED 0.85]
- **Monitoring-Set: 3 überwachte Temp-Ordner + Gesamtbilanz** — assets_screenshot_percent_temp, assets_screenshot_localappdata_temp, assets_screenshot_systemroot_temp, assets_screenshot_gesamt_card [EXTRACTED 1.00]
- **Scan-Aktions-Workflow: Aktualisieren → Temp/Alle löschen → Statusanzeige** — assets_screenshot_aktualisieren_button, assets_screenshot_temp_loschen_button, assets_screenshot_alle_loeschen_button, assets_screenshot_status_bar [INFERRED 0.85]

## Communities (15 total, 6 thin omitted)

### Community 0 - "Tk-Event-Handler & Module"
Cohesion: 0.08
Nodes (20): customtkinter, queue, Event-Test: Tkinter/CTk-Events unter Python 3.14 + Tk 9.0., check(), _de(), _dev_screenshot(), format_bytes(), main() (+12 more)

### Community 1 - "Win32-CTypes-Strukturen & E2E-Test"
Cohesion: 0.09
Nodes (22): ctypes, ctypes_wintypes, importlib_util, os, INPUT_, MOUSEINPUT, POINT, End-to-End: echte TempApp + ECHTER Mausklick (SendInput) auf 'Aktualisieren'.… (+14 more)

### Community 2 - "Design-System & Design-Doku"
Cohesion: 0.15
Nodes (26): DESIGN.md — Temp-Reiniger Design-System, Auto-Re-Scan nach dem Löschen (~3 s), Design-Richtung 'The Scale', Layout/Komposition: Kopfzeile, drei Karten nebeneinander, Gesamt-Zeile, Fußstatusleiste, Motion-Grammatik (Count-up beim Scan, Tween-Abfall nach dem Löschen, Zwei-Stufen-Armierung), Farbpalette (Slate #E9EDF3, Card-Weiß, Teal-Akzent #1296B0, OK-Grün, Warn-Amber), Sicherheitsregeln (gebaut), Signatur: relative Füllstand-Leiste + große Bahnschrift-Zahl (+18 more)

### Community 3 - "Loesch-Logik & Worker"
Cohesion: 0.20
Nodes (5): delete_folder_contents(), format_count(), Nur den INHALT von `top` löschen. `top` selbst bleibt bestehen. Rückgabe:…, Ordner nach Lösch-Aktion automatisch neu einscannen. Kurze Verzögerung, damit…, Unerwarteter Fehler im Delete-Worker: UI wieder freigeben (Main-Thread).

### Community 4 - "Screenshot: Karten & Status"
Cohesion: 0.24
Nodes (12): 'Aktualisieren'-Button in der Kopfzeile, 'Alle löschen'-Button (Gesamt), Gesamt-Karte: GESAMT · ALLE TEMP-ORDNER (3,36 GB), %LOCALAPPDATA%\Temp (C:\Users\hundsbuah\AppData\Local\Temp) — 774,38 MB, 389 Dateien, %TEMP% (E:\Windows\Temp) — 2,18 GB, 1 244 Dateien, Größenbalken unter jeder Ordner-Karte, Scan/Refresh-Mechanismus (zeitgestempeltes Einlesen der Temp-Ordner), Statusleiste: Bereit · eingelesen 14:17 · vor 0 Sekunden · 3,36 GB gesamt (+4 more)

### Community 5 - "TempApp-Kern & Armierung"
Cohesion: 0.24
Nodes (3): Zwei-Stufen-Bestätigung: Button kurz armieren., Minimieren -> in den Tray verschwinden (Fenster ausblenden)., TempApp

### Community 6 - "Screenshot: Aktionen & Layout"
Cohesion: 0.44
Nodes (11): 'Aktualisieren' Refresh Action, 'Alle löschen' Delete-All Action, 'Temp löschen' Per-Folder Delete Action, %LOCALAPPDATA%\Temp Card (C:\Users\hundsbuah\AppData\Local\Temp), %SystemRoot%\Temp Card (C:\WINDOWS\Temp), %TEMP% Temp-Folder Card (E:\Windows\Temp), Three-Column Card Grid Layout, Relative-Size Progress Bar (+3 more)

### Community 7 - "App-Start, Poller & Tray-Thread"
Cohesion: 0.18
Nodes (5): Zentrieren über den gesamten VIRTUELLEN Schreibtisch (Multi-Monitor), nicht nur…, Zeitstempel als „vor X Sekunden/Minuten/Stunden" (deutsch)., Refresh-Feedback: aktualisiert „vor X Sekunden" (nur Bereit-Zustand)., System-Tray-Icon in einem eigenen Thread starten (Windows)., Haupt-Thread-Poller: führt Main-Thread-Kommandos sicher im Tk-Thread aus. Tray-…

### Community 11 - "Produkt-Dokumentation"
Cohesion: 0.70
Nodes (5): PRODUCT — Temp-Reiniger, Chosen Direction: The Scale, Product Constraints, Three Temp Folders, Temp-Reiniger

## Knowledge Gaps
- **10 isolated node(s):** `POINT`, `MOUSEINPUT`, `_U`, `MOUSEINPUT`, `_U` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 51 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TempApp` connect `TempApp-Kern & Armierung` to `Tk-Event-Handler & Module`, `Loesch-Logik & Worker`, `App-Start, Poller & Tray-Thread`, `Tray-Menue & Aktionen`, `UI-Aufbau & Temp-Definitionen`, `Delete-Flow & Bestaetigung`?**
  _High betweenness centrality (0.261) - this node is a cross-community bridge._
- **Why does `Tooltip` connect `Tooltip-Komponente` to `Tk-Event-Handler & Module`, `TempApp-Kern & Armierung`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `format_bytes()` connect `Tk-Event-Handler & Module` to `Loesch-Logik & Worker`, `App-Start, Poller & Tray-Thread`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `README.md — Temp-Reiniger (Produkt-Dokumentation)` (e.g. with `Auto-Re-Scan nach dem Löschen (~3 s)` and `Sicherheitsregeln (gebaut)`) actually correct?**
  _`README.md — Temp-Reiniger (Produkt-Dokumentation)` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `POINT`, `MOUSEINPUT`, `_U` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Tk-Event-Handler & Module` be split into smaller, more focused modules?**
  _Cohesion score 0.07936507936507936 - nodes in this community are weakly interconnected._
- **Should `Win32-CTypes-Strukturen & E2E-Test` be split into smaller, more focused modules?**
  _Cohesion score 0.09401709401709402 - nodes in this community are weakly interconnected._