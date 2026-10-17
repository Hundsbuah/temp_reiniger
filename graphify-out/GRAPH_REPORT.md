# Graph Report - temp_delete  (2026-10-17)

## Corpus Check
- 9 files · ~16,090 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .spec 1)

## Summary
- 260 nodes · 437 edges · 20 communities (8 shown, 12 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 41 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `51378ac0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TempApp
- _review_e2e_test.py
- Temp-Reiniger (README)
- temp_reiniger.py
- Temp-Ordner-Karte (wiederkehrende Komponente)
- %LOCALAPPDATA%\Temp Card (C:\Users\hundsbuah\AppData\Local\Temp)
- Tooltip
- Tray Icon — White Trash Can on Teal Rounded Square
- Tray Icon (white trash bin on rounded teal tile)
- Installation: fertige EXE via GitHub-Release (Option A)
- ._scan_all
- delete_folder_contents
- ._on_scanned
- requirements.txt — Laufzeit-Abhängigkeiten
- ._on_all_delete
- run

## God Nodes (most connected - your core abstractions)
1. `TempApp` - 47 edges
2. `Temp-Reiniger (README)` - 10 edges
3. `delete_folder_contents()` - 9 edges
4. `Temp-Reiniger (App)` - 9 edges
5. `Temp-Reiniger (Produkt)` - 9 edges
6. `click_nein()` - 8 edges
7. `format_bytes()` - 7 edges
8. `scan_folder()` - 7 edges
9. `_log_error()` - 7 edges
10. `_is_reparse_point()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `EXE selbst bauen (PyInstaller --onefile)` --conceptually_related_to--> `Temp-Reiniger (Produkt)`  [INFERRED]
  README.md → PRODUCT.md
- `Sicherheitsregeln` --semantically_similar_to--> `Constraints`  [INFERRED] [semantically similar]
  DESIGN.md → PRODUCT.md
- `Sicherheit` --semantically_similar_to--> `Sicherheitsregeln`  [INFERRED] [semantically similar]
  README.md → DESIGN.md
- `Sicherheit` --semantically_similar_to--> `Constraints`  [INFERRED] [semantically similar]
  README.md → PRODUCT.md
- `Chosen Direction: The Scale` --conceptually_related_to--> `Direction: The Scale`  [INFERRED]
  PRODUCT.md → DESIGN.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Monitoring-Set: 3 überwachte Temp-Ordner + Gesamtbilanz** — assets_screenshot_percent_temp, assets_screenshot_localappdata_temp, assets_screenshot_systemroot_temp, assets_screenshot_gesamt_card [EXTRACTED 1.00]
- **Design-Richtung 'The Scale' (Signature + Memorable Moment)** — design_direction_the_scale, design_signature_fillbar, product_direction_the_scale, product_memorable_moment_leerziehen [INFERRED 0.75]
- **Scan-Aktions-Workflow: Aktualisieren → Temp/Alle löschen → Statusanzeige** — assets_screenshot_aktualisieren_button, assets_screenshot_temp_loschen_button, assets_screenshot_alle_loeschen_button, assets_screenshot_status_bar [INFERRED 0.85]
- **Duplikat-Handling: %TEMP% ≡ %LOCALAPPDATA%\Temp** — product_temp_localappdata_duplication, readme_duplicate_detection, design_duplicate_hint [INFERRED 0.85]
- **Sicherheitsregeln-Regelwerk (Sicherheit, Constraints, Sicherheitsregeln)** — design_security_rules, product_constraints, readme_security [INFERRED 0.85]
- **Temp-Folder Card Grid (3 Standard Windows Temp Locations)** — _impeccable_review_desktop_card_temp, _impeccable_review_desktop_card_localappdata_temp, _impeccable_review_desktop_card_systemroot_temp [INFERRED 0.85]

## Communities (20 total, 12 thin omitted)

### Community 1 - "_review_e2e_test.py"
Cohesion: 0.06
Nodes (23): _abs(), _bring_ensure(), HARDWAREINPUT, INPUT_, _U, KEYBDINPUT, MOUSEINPUT, POINT (+15 more)

### Community 2 - "Temp-Reiniger (README)"
Cohesion: 0.08
Nodes (26): Direction: The Scale, Duplikat-Hinweis (zwei Pfade, ein Ordner), Layout / Komposition (3 Karten), Motion-Grammatik, Palette (Slate, Teal-Akzent), Signatur: relative Füllstand-Leiste + große Bahnschrift-Zahl, UI-Zustände (Scan, Bereit, armiert, entfernt, übersprungen), System-Tray (Minimieren, Rechtsklick-Menü) (+18 more)

### Community 3 - "temp_reiniger.py"
Cohesion: 0.08
Nodes (7): _acquire_instance_mutex(), _de(), _dev_screenshot(), main(), run_capture(), _plural_de(), validate_temp_path()

### Community 5 - "Temp-Ordner-Karte (wiederkehrende Komponente)"
Cohesion: 0.24
Nodes (11): 'Aktualisieren'-Button in der Kopfzeile, 'Alle löschen'-Button (Gesamt), Gesamt-Karte: GESAMT · ALLE TEMP-ORDNER (3,36 GB), %LOCALAPPDATA%\Temp (C:\Users\hundsbuah\AppData\Local\Temp) — 774,38 MB, 389 Dateien, %TEMP% (E:\Windows\Temp) — 2,18 GB, 1 244 Dateien, Größenbalken unter jeder Ordner-Karte, Statusleiste: Bereit · eingelesen 14:17 · vor 0 Sekunden · 3,36 GB gesamt, %SystemRoot%\Temp (C:\WINDOWS\Temp) — 434,88 MB, 207 Dateien (+3 more)

### Community 6 - "%LOCALAPPDATA%\Temp Card (C:\Users\hundsbuah\AppData\Local\Temp)"
Cohesion: 0.44
Nodes (11): 'Aktualisieren' Refresh Action, 'Alle löschen' Delete-All Action, 'Temp löschen' Per-Folder Delete Action, %LOCALAPPDATA%\Temp Card (C:\Users\hundsbuah\AppData\Local\Temp), %SystemRoot%\Temp Card (C:\WINDOWS\Temp), %TEMP% Temp-Folder Card (E:\Windows\Temp), Three-Column Card Grid Layout, Relative-Size Progress Bar (+3 more)

### Community 13 - "delete_folder_contents"
Cohesion: 0.18
Nodes (9): delete_folder_contents(), _recover_hostile(), _is_reparse_point(), scan_folder(), _onerror(), _recover_scan(), _err(), _under_blocked() (+1 more)

### Community 15 - "._on_scanned"
Cohesion: 0.24
Nodes (4): format_bytes(), format_count(), _log_error(), step()

### Community 17 - "requirements.txt — Laufzeit-Abhängigkeiten"
Cohesion: 0.40
Nodes (5): requirements.txt — Laufzeit-Abhängigkeiten, customtkinter (>=5.2) — UI-Framework, Pillow (>=10.0) — Tray-Icon / Dev, PyInstaller (>=6.0, nur EXE-Build), pystray (>=0.19) — System-Tray

## Knowledge Gaps
- **12 isolated node(s):** `Installation: fertige EXE via GitHub-Release (Option A)`, `customtkinter (>=5.2) — UI-Framework`, `Pillow (>=10.0) — Tray-Icon / Dev`, `PyInstaller (>=6.0, nur EXE-Build)`, `pystray (>=0.19) — System-Tray` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 96 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TempApp` connect `TempApp` to `temp_reiniger.py`, `.__init__`, `._set_status`, `._scan_all`, `._set_busy`, `._on_scanned`, `._status_ticker`, `._on_all_delete`, `run`?**
  _High betweenness centrality (0.267) - this node is a cross-community bridge._
- **What connects `Installation: fertige EXE via GitHub-Release (Option A)`, `customtkinter (>=5.2) — UI-Framework`, `Pillow (>=10.0) — Tray-Icon / Dev` to the rest of the system?**
  _12 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `_review_e2e_test.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05513784461152882 - nodes in this community are weakly interconnected._
- **Why does `Tooltip` connect `Tooltip` to `TempApp`, `temp_reiniger.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Should `Temp-Reiniger (README)` be split into smaller, more focused modules?**
  _Cohesion score 0.07682926829268293 - nodes in this community are weakly interconnected._
- **Why does `delete_folder_contents()` connect `delete_folder_contents` to `temp_reiniger.py`, `._on_scanned`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `temp_reiniger.py` be split into smaller, more focused modules?**
  _Cohesion score 0.082010582010582 - nodes in this community are weakly interconnected._