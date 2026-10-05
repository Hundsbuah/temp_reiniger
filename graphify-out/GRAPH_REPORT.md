# Graph Report - temp_delete  (2026-10-05)

## Corpus Check
- 8 files · ~8,546 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .spec 1)

## Summary
- 156 nodes · 251 edges · 9 communities (7 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.83)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `43225a9a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- temp_reiniger.py
- _review_tray_test.py
- format_bytes
- PRODUCT — Temp-Reiniger
- ._build_menu
- 🧹 Temp-Reiniger
- DESIGN — Temp-Reiniger (gebaut)
- TempApp
- Tooltip

## God Nodes (most connected - your core abstractions)
1. `TempApp` - 39 edges
2. `DESIGN — Temp-Reiniger (gebaut)` - 10 edges
3. `🧹 Temp-Reiniger` - 10 edges
4. `click_nein()` - 7 edges
5. `format_bytes()` - 6 edges
6. `Tooltip` - 6 edges
7. `PRODUCT — Temp-Reiniger` - 5 edges
8. `click()` - 4 edges
9. `scan_folder()` - 4 edges
10. `delete_folder_contents()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Desktop Screenshot` --references--> `PRODUCT — Temp-Reiniger`  [INFERRED]
  .impeccable/review/desktop.png → PRODUCT.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Temp-Reiniger Product Specification** — product, product_temp_reiniger, product_temp_folders, product_constraints, product_chosen_direction [INFERRED 0.80]

## Communities (9 total, 2 thin omitted)

### Community 0 - "temp_reiniger.py"
Cohesion: 0.09
Nodes (6): minimize_check(), delete_folder_contents(), _dev_screenshot(), main(), run_capture(), scan_folder()

### Community 1 - "_review_tray_test.py"
Cohesion: 0.10
Nodes (12): INPUT_, MOUSEINPUT, POINT, real_click(), ev(), _U, click(), ev() (+4 more)

### Community 3 - "PRODUCT — Temp-Reiniger"
Cohesion: 0.53
Nodes (6): Desktop Screenshot, PRODUCT — Temp-Reiniger, Chosen Direction: The Scale, Product Constraints, Three Temp Folders, Temp-Reiniger

### Community 4 - "._build_menu"
Cohesion: 0.12
Nodes (3): make_tray_icon(), temp_definitions(), run()

### Community 5 - "🧹 Temp-Reiniger"
Cohesion: 0.17
Nodes (12): 🧱 Aufbau, 🎨 Design, 📦 EXE selbst bauen (PyInstaller), ✨ Features, ⚙️ Hinweise, 🚀 Installation & Start, 📄 Lizenz, Option A — Fertige EXE (empfohlen) (+4 more)

### Community 6 - "DESIGN — Temp-Reiniger (gebaut)"
Cohesion: 0.17
Nodes (10): DESIGN — Temp-Reiniger (gebaut), Direction: „The Scale", Layout / Komposition, Motion-Grammatik, Palette (eigene Welt — mit Inhalt entfernt noch erkennbar), Sicherheitsregeln (gebaut), Signature (das Memorale), System-Tray (Minimieren / Rechtsklick) (+2 more)

### Community 7 - "TempApp"
Cohesion: 0.10
Nodes (5): format_count(), TempApp, revert(), do(), step()

## Knowledge Gaps
- **23 isolated node(s):** `POINT`, `_U`, `_U`, `Direction: „The Scale"`, `Palette (eigene Welt — mit Inhalt entfernt noch erkennbar)` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 67 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TempApp` connect `TempApp` to `temp_reiniger.py`, `format_bytes`, `._build_menu`?**
  _High betweenness centrality (0.376) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `click_nein()` (e.g. with `child_cb()` and `enum_cb()`) actually correct?**
  _`click_nein()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `POINT`, `_U`, `_U` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `temp_reiniger.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09333333333333334 - nodes in this community are weakly interconnected._
- **Why does `Tooltip` connect `Tooltip` to `temp_reiniger.py`, `TempApp`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Should `_review_tray_test.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0989247311827957 - nodes in this community are weakly interconnected._
- **Should `._build_menu` be split into smaller, more focused modules?**
  _Cohesion score 0.12418300653594772 - nodes in this community are weakly interconnected._