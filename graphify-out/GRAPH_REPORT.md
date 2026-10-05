# Graph Report - temp_delete  (2026-10-05)

## Corpus Check
- Corpus is ~9,727 words - fits in a single context window. You may not need a graph.

## Summary
- 208 nodes · 355 edges · 12 communities (7 shown, 5 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.86)
- Token cost: 41,927 input · 0 output

## Community Hubs (Navigation)
- Kern-Utilities & Tween/Rescan
- Win32-CTypes & E2E-Tests
- Design-System & Design-Doku
- App-Kern & Loesch-Logik
- Tray, Poller & App-Start
- Screenshot: Karten & Status
- Screenshot: Aktionen & Layout
- Verhaltens-Spezifikation (Motion/Zustaende)
- Tooltip-Komponente
- Tray-Icon-Semantik
- Tray-Icon-Datei
- EXE-Verteilung (GitHub-Release)

## God Nodes (most connected - your core abstractions)
1. `TempApp` - 40 edges
2. `Temp-Reiniger (README)` - 10 edges
3. `Temp-Reiniger (App)` - 9 edges
4. `Temp-Reiniger (Produkt)` - 9 edges
5. `click_nein()` - 7 edges
6. `UI-Zustände (Scan, Bereit, armiert, entfernt, übersprungen)` - 6 edges
7. `format_bytes()` - 6 edges
8. `Tooltip` - 6 edges
9. `Sicherheitsregeln` - 6 edges
10. `Temp-Reiniger Desktop UI (Screenshot)` - 6 edges

## Surprising Connections (you probably didn't know these)
- `UI-Zustände (Scan, Bereit, armiert, entfernt, übersprungen)` --references--> `Duplikat-Erkennung (leert nur einmal)`  [INFERRED]
  DESIGN.md → README.md
- `Abhängigkeiten (customtkinter, pystray, pywin32, Pillow)` --conceptually_related_to--> `Annahmen`  [INFERRED]
  README.md → PRODUCT.md
- `Sicherheitsregeln` --semantically_similar_to--> `Constraints`  [INFERRED] [semantically similar]
  DESIGN.md → PRODUCT.md
- `Sicherheit` --semantically_similar_to--> `Sicherheitsregeln`  [INFERRED] [semantically similar]
  README.md → DESIGN.md
- `Sicherheit` --semantically_similar_to--> `Constraints`  [INFERRED] [semantically similar]
  README.md → PRODUCT.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sicherheitsregeln-Regelwerk (Sicherheit, Constraints, Sicherheitsregeln)** — design_security_rules, product_constraints, readme_security [INFERRED 0.85]
- **Duplikat-Handling: %TEMP% ≡ %LOCALAPPDATA%\Temp** — product_temp_localappdata_duplication, readme_duplicate_detection, design_duplicate_hint [INFERRED 0.85]
- **Design-Richtung 'The Scale' (Signature + Memorable Moment)** — design_direction_the_scale, design_signature_fillbar, product_direction_the_scale, product_memorable_moment_leerziehen [INFERRED 0.75]
- **Temp-Folder Card Grid (3 Standard Windows Temp Locations)** — _impeccable_review_desktop_card_temp, _impeccable_review_desktop_card_localappdata_temp, _impeccable_review_desktop_card_systemroot_temp [INFERRED 0.85]
- **Monitoring-Set: 3 überwachte Temp-Ordner + Gesamtbilanz** — assets_screenshot_percent_temp, assets_screenshot_localappdata_temp, assets_screenshot_systemroot_temp, assets_screenshot_gesamt_card [EXTRACTED 1.00]
- **Scan-Aktions-Workflow: Aktualisieren → Temp/Alle löschen → Statusanzeige** — assets_screenshot_aktualisieren_button, assets_screenshot_temp_loschen_button, assets_screenshot_alle_loeschen_button, assets_screenshot_status_bar [INFERRED 0.85]

## Communities (12 total, 5 thin omitted)

### Community 0 - "Kern-Utilities & Tween/Rescan"
Cohesion: 0.08
Nodes (7): format_count(), _plural_de(), temp_definitions(), TempApp, revert(), do(), step()

### Community 1 - "Win32-CTypes & E2E-Tests"
Cohesion: 0.07
Nodes (14): _abs(), INPUT_, MOUSEINPUT, POINT, real_click(), ev(), _U, minimize_check() (+6 more)

### Community 2 - "Design-System & Design-Doku"
Cohesion: 0.09
Nodes (28): Direction: The Scale, Duplikat-Hinweis (zwei Pfade, ein Ordner), Layout / Komposition (3 Karten), Palette (Slate, Teal-Akzent), Signatur: relative Füllstand-Leiste + große Bahnschrift-Zahl, System-Tray (Minimieren, Rechtsklick-Menü), Temp-Reiniger (App), Typografie (Bahnschrift, Consolas, Segoe UI) (+20 more)

### Community 3 - "App-Kern & Loesch-Logik"
Cohesion: 0.11
Nodes (9): _watchdog(), _de(), delete_folder_contents(), _dev_screenshot(), format_bytes(), _is_reparse_point(), main(), run_capture() (+1 more)

### Community 5 - "Screenshot: Karten & Status"
Cohesion: 0.24
Nodes (11): 'Aktualisieren'-Button in der Kopfzeile, 'Alle löschen'-Button (Gesamt), Gesamt-Karte: GESAMT · ALLE TEMP-ORDNER (3,36 GB), %LOCALAPPDATA%\Temp (C:\Users\hundsbuah\AppData\Local\Temp) — 774,38 MB, 389 Dateien, %TEMP% (E:\Windows\Temp) — 2,18 GB, 1 244 Dateien, Größenbalken unter jeder Ordner-Karte, Statusleiste: Bereit · eingelesen 14:17 · vor 0 Sekunden · 3,36 GB gesamt, %SystemRoot%\Temp (C:\WINDOWS\Temp) — 434,88 MB, 207 Dateien (+3 more)

### Community 6 - "Screenshot: Aktionen & Layout"
Cohesion: 0.44
Nodes (11): 'Aktualisieren' Refresh Action, 'Alle löschen' Delete-All Action, 'Temp löschen' Per-Folder Delete Action, %LOCALAPPDATA%\Temp Card (C:\Users\hundsbuah\AppData\Local\Temp), %SystemRoot%\Temp Card (C:\WINDOWS\Temp), %TEMP% Temp-Folder Card (E:\Windows\Temp), Three-Column Card Grid Layout, Relative-Size Progress Bar (+3 more)

### Community 7 - "Verhaltens-Spezifikation (Motion/Zustaende)"
Cohesion: 0.36
Nodes (3): Motion-Grammatik, UI-Zustände (Scan, Bereit, armiert, entfernt, übersprungen), Features

## Knowledge Gaps
- **11 isolated node(s):** `Installation: fertige EXE via GitHub-Release (Option A)`, `Typografie (Bahnschrift, Consolas, Segoe UI)`, `POINT`, `_U`, `_U` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 62 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TempApp` connect `Kern-Utilities & Tween/Rescan` to `App-Kern & Loesch-Logik`, `Tray, Poller & App-Start`?**
  _High betweenness centrality (0.236) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Temp-Reiniger (Produkt)` (e.g. with `Temp-Reiniger (App)` and `EXE selbst bauen (PyInstaller --onefile)`) actually correct?**
  _`Temp-Reiniger (Produkt)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Installation: fertige EXE via GitHub-Release (Option A)`, `Typografie (Bahnschrift, Consolas, Segoe UI)`, `POINT` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Kern-Utilities & Tween/Rescan` be split into smaller, more focused modules?**
  _Cohesion score 0.07755102040816327 - nodes in this community are weakly interconnected._
- **Why does `Tooltip` connect `Tooltip-Komponente` to `Kern-Utilities & Tween/Rescan`, `App-Kern & Loesch-Logik`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Should `Win32-CTypes & E2E-Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.07084785133565621 - nodes in this community are weakly interconnected._
- **Why does `Temp-Reiniger (README)` connect `Design-System & Design-Doku` to `Verhaltens-Spezifikation (Motion/Zustaende)`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._