# Graph Report - temp_delete  (2026-08-30)

## Corpus Check
- 3 files · ~3,638 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 58 nodes · 95 edges · 9 communities (4 shown, 5 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- temp_reiniger.py
- ._do_delete
- PRODUCT — Temp-Reiniger
- ._build_ui
- ._build_card
- DESIGN — Temp-Reiniger (gebaut)
- TempApp
- delete_folder_contents

## God Nodes (most connected - your core abstractions)
1. `TempApp` - 24 edges
2. `DESIGN — Temp-Reiniger (gebaut)` - 9 edges
3. `format_bytes()` - 5 edges
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

## Communities (9 total, 5 thin omitted)

### Community 0 - "temp_reiniger.py"
Cohesion: 0.18
Nodes (10): _de(), _dev_screenshot(), format_bytes(), format_count(), main(), (gesamte Gröe in Byte, Dateianzahl) eines Ordners zählen. Fehler (z. B.…, Fenster rendern, Größen setzen (echtes Einlesen oder Mock), speichern., Zahl im deutschen Format: Tausender-Dürrraum, Dezimalkomma. (+2 more)

### Community 3 - "PRODUCT — Temp-Reiniger"
Cohesion: 0.53
Nodes (6): Desktop Screenshot, PRODUCT — Temp-Reiniger, Chosen Direction: The Scale, Product Constraints, Three Temp Folders, Temp-Reiniger

### Community 6 - "DESIGN — Temp-Reiniger (gebaut)"
Cohesion: 0.20
Nodes (9): DESIGN — Temp-Reiniger (gebaut), Direction: „The Scale", Layout / Komposition, Motion-Grammatik, Palette (eigene Welt — mit Inhalt entfernt noch erkennbar), Sicherheitsregeln (gebaut), Signature (das Memorale), Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling) (+1 more)

## Knowledge Gaps
- **9 isolated node(s):** `Direction: „The Scale"`, `Palette (eigene Welt — mit Inhalt entfernt noch erkennbar)`, `Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling)`, `Layout / Komposition`, `Signature (das Memorale)` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TempApp` connect `TempApp` to `temp_reiniger.py`, `._do_delete`, `._on_deleted`, `._build_ui`, `._build_card`, `delete_folder_contents`?**
  _High betweenness centrality (0.311) - this node is a cross-community bridge._
- **Why does `Tooltip` connect `._build_card` to `temp_reiniger.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `format_bytes()` connect `temp_reiniger.py` to `._on_deleted`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **What connects `Direction: „The Scale"`, `Palette (eigene Welt — mit Inhalt entfernt noch erkennbar)`, `Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling)` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._