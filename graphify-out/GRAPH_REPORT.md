# Graph Report - temp_delete  (2026-08-30)

## Corpus Check
- 3 files · ~4,031 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 66 nodes · 111 edges · 8 communities (5 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `86019ea5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- temp_reiniger.py
- ._on_deleted
- ._status_ticker
- PRODUCT — Temp-Reiniger
- ._build_ui
- ._on_scanned
- DESIGN — Temp-Reiniger (gebaut)
- TempApp

## God Nodes (most connected - your core abstractions)
1. `TempApp` - 28 edges
2. `DESIGN — Temp-Reiniger (gebaut)` - 9 edges
3. `format_bytes()` - 6 edges
4. `Tooltip` - 5 edges
5. `PRODUCT — Temp-Reiniger` - 5 edges
6. `Temp-Reiniger` - 4 edges
7. `_de()` - 3 edges
8. `format_count()` - 3 edges
9. `scan_folder()` - 3 edges
10. `delete_folder_contents()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `Desktop Screenshot` --references--> `PRODUCT — Temp-Reiniger`  [INFERRED]
  .impeccable/review/desktop.png → PRODUCT.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Temp-Reiniger Product Specification** — product, product_temp_reiniger, product_temp_folders, product_constraints, product_chosen_direction [INFERRED 0.80]

## Communities (8 total, 3 thin omitted)

### Community 0 - "temp_reiniger.py"
Cohesion: 0.18
Nodes (8): _de(), _dev_screenshot(), format_bytes(), main(), Fenster rendern, Größen setzen (echtes Einlesen oder Mock), speichern., Zahl im deutschen Format: Tausender-Dürrraum, Dezimalkomma., Byte-Größe als lesbare Zeichenfolge (deutsche Konvention)., Tooltip

### Community 1 - "._on_deleted"
Cohesion: 0.29
Nodes (4): delete_folder_contents(), format_count(), Nur den INHALT von `top` löschen. `top` selbst bleibt bestehen. Rückgabe:…, Ordner nach Lösch-Aktion automatisch neu einscannen. Kurze Verzögerung, damit…

### Community 3 - "PRODUCT — Temp-Reiniger"
Cohesion: 0.53
Nodes (6): Desktop Screenshot, PRODUCT — Temp-Reiniger, Chosen Direction: The Scale, Product Constraints, Three Temp Folders, Temp-Reiniger

### Community 6 - "DESIGN — Temp-Reiniger (gebaut)"
Cohesion: 0.20
Nodes (9): DESIGN — Temp-Reiniger (gebaut), Direction: „The Scale", Layout / Komposition, Motion-Grammatik, Palette (eigene Welt — mit Inhalt entfernt noch erkennbar), Sicherheitsregeln (gebaut), Signature (das Memorale), Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling) (+1 more)

### Community 7 - "TempApp"
Cohesion: 0.25
Nodes (3): Angehängten Auto-Rescan (nach Lösch-Aktion) abbrechen., Zwei-Stufen-Bestätigung: Button kurz armieren., TempApp

## Knowledge Gaps
- **9 isolated node(s):** `Direction: „The Scale"`, `Palette (eigene Welt — mit Inhalt entfernt noch erkennbar)`, `Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling)`, `Layout / Komposition`, `Signature (das Memorale)` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TempApp` connect `TempApp` to `temp_reiniger.py`, `._on_deleted`, `._status_ticker`, `._build_ui`, `._on_scanned`?**
  _High betweenness centrality (0.372) - this node is a cross-community bridge._
- **Why does `Tooltip` connect `temp_reiniger.py` to `TempApp`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `format_bytes()` connect `temp_reiniger.py` to `._on_deleted`, `._status_ticker`, `._on_scanned`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **What connects `Direction: „The Scale"`, `Palette (eigene Welt — mit Inhalt entfernt noch erkennbar)`, `Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling)` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._