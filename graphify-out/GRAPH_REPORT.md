# Graph Report - temp_delete  (2026-08-30)

## Corpus Check
- 3 files · ~3,904 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 62 nodes · 103 edges · 8 communities (4 shown, 4 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `be77c649`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- temp_reiniger.py
- ._build_card
- ._on_deleted
- PRODUCT — Temp-Reiniger
- ._build_ui
- ._on_scanned
- DESIGN — Temp-Reiniger (gebaut)
- TempApp

## God Nodes (most connected - your core abstractions)
1. `TempApp` - 26 edges
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

## Communities (8 total, 4 thin omitted)

### Community 0 - "temp_reiniger.py"
Cohesion: 0.14
Nodes (10): _de(), delete_folder_contents(), _dev_screenshot(), format_bytes(), main(), Nur den INHALT von `top` löschen. `top` selbst bleibt bestehen. Rückgabe:…, Fenster rendern, Größen setzen (echtes Einlesen oder Mock), speichern., Zahl im deutschen Format: Tausender-Dürrraum, Dezimalkomma. (+2 more)

### Community 3 - "PRODUCT — Temp-Reiniger"
Cohesion: 0.53
Nodes (6): Desktop Screenshot, PRODUCT — Temp-Reiniger, Chosen Direction: The Scale, Product Constraints, Three Temp Folders, Temp-Reiniger

### Community 5 - "._on_scanned"
Cohesion: 0.33
Nodes (3): format_count(), (gesamte Gröe in Byte, Dateianzahl) eines Ordners zählen. Fehler (z. B.…, scan_folder()

### Community 6 - "DESIGN — Temp-Reiniger (gebaut)"
Cohesion: 0.20
Nodes (9): DESIGN — Temp-Reiniger (gebaut), Direction: „The Scale", Layout / Komposition, Motion-Grammatik, Palette (eigene Welt — mit Inhalt entfernt noch erkennbar), Sicherheitsregeln (gebaut), Signature (das Memorale), Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling) (+1 more)

## Knowledge Gaps
- **9 isolated node(s):** `Direction: „The Scale"`, `Palette (eigene Welt — mit Inhalt entfernt noch erkennbar)`, `Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling)`, `Layout / Komposition`, `Signature (das Memorale)` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TempApp` connect `TempApp` to `temp_reiniger.py`, `._build_card`, `._on_deleted`, `._build_ui`, `._on_scanned`?**
  _High betweenness centrality (0.339) - this node is a cross-community bridge._
- **Why does `Tooltip` connect `temp_reiniger.py` to `._build_card`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `format_bytes()` connect `temp_reiniger.py` to `._on_deleted`, `._on_scanned`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **What connects `Direction: „The Scale"`, `Palette (eigene Welt — mit Inhalt entfernt noch erkennbar)`, `Typografie (native Windows-Fonts → Single-EXE ohne Font-Bundling)` to the rest of the system?**
  _9 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `temp_reiniger.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._