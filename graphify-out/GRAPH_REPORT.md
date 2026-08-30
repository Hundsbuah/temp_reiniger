# Graph Report - temp_delete  (2026-08-30)

## Corpus Check
- 3 files · ~4,546 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 83 nodes · 136 edges · 8 communities (5 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0f0ce78a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- temp_reiniger.py
- ._build_menu
- .__init__
- PRODUCT — Temp-Reiniger
- ._build_ui
- ._on_unmap
- DESIGN — Temp-Reiniger (gebaut)
- TempApp

## God Nodes (most connected - your core abstractions)
1. `TempApp` - 37 edges
2. `DESIGN — Temp-Reiniger (gebaut)` - 10 edges
3. `format_bytes()` - 6 edges
4. `Tooltip` - 5 edges
5. `PRODUCT — Temp-Reiniger` - 5 edges
6. `temp_definitions()` - 4 edges
7. `Temp-Reiniger` - 4 edges
8. `_de()` - 3 edges
9. `format_count()` - 3 edges
10. `scan_folder()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `Desktop Screenshot` --references--> `PRODUCT — Temp-Reiniger`  [INFERRED]
  .impeccable/review/desktop.png → PRODUCT.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Temp-Reiniger Product Specification** — product, product_temp_reiniger, product_temp_folders, product_constraints, product_chosen_direction [INFERRED 0.80]

## Communities (8 total, 3 thin omitted)

### Community 0 - "temp_reiniger.py"
Cohesion: 0.12
Nodes (14): _de(), delete_folder_contents(), _dev_screenshot(), format_bytes(), format_count(), main(), make_tray_icon(), (gesamte Gröe in Byte, Dateianzahl) eines Ordners zählen. Fehler (z. B.… (+6 more)

### Community 2 - ".__init__"
Cohesion: 0.20
Nodes (4): Zeitstempel als „vor X Sekunden/Minuten/Stunden" (deutsch)., Refresh-Feedback: aktualisiert „vor X Sekunden" (nur Bereit-Zustand)., System-Tray-Icon in einem eigenen Thread starten (Windows)., Haupt-Thread-Poller: führt Tray-Aktionen sicher im Tk-Thread aus.

### Community 3 - "PRODUCT — Temp-Reiniger"
Cohesion: 0.53
Nodes (6): Desktop Screenshot, PRODUCT — Temp-Reiniger, Chosen Direction: The Scale, Product Constraints, Three Temp Folders, Temp-Reiniger

### Community 6 - "DESIGN — Temp-Reiniger (gebaut)"
Cohesion: 0.18
Nodes (10): DESIGN — Temp-Reiniger (gebaut), Direction: „The Scale", Layout / Komposition, Motion-Grammatik, Palette (eigene Welt — mit Inhalt entfernt noch erkennbar), Sicherheitsregeln (gebaut), Signature (das Memorale), System-Tray (Minimieren / Rechtsklick) (+2 more)

### Community 7 - "TempApp"
Cohesion: 0.20
Nodes (4): Angehängten Auto-Rescan (nach Lösch-Aktion) abbrechen., Ordner nach Lösch-Aktion automatisch neu einscannen. Kurze Verzögerung, damit…, Zwei-Stufen-Bestätigung: Button kurz armieren., TempApp

## Knowledge Gaps
- **10 isolated node(s):** `Direction: „The Scale"`, `Palette (eigene Welt — mit Inhalt entfernt noch erkennbar)`, `Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling)`, `Layout / Komposition`, `Signature (das Memorale)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TempApp` connect `TempApp` to `temp_reiniger.py`, `._build_menu`, `.__init__`, `._build_ui`, `._on_unmap`?**
  _High betweenness centrality (0.471) - this node is a cross-community bridge._
- **Why does `Tooltip` connect `._build_ui` to `temp_reiniger.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `format_bytes()` connect `temp_reiniger.py` to `.__init__`, `TempApp`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **What connects `Direction: „The Scale"`, `Palette (eigene Welt — mit Inhalt entfernt noch erkennbar)`, `Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling)` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `temp_reiniger.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12280701754385964 - nodes in this community are weakly interconnected._