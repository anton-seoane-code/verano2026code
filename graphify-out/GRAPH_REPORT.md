# Graph Report - .  (2026-06-18)

## Corpus Check
- Corpus is ~2,667 words - fits in a single context window. You may not need a graph.

## Summary
- 48 nodes · 66 edges · 7 communities (5 shown, 2 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Todo List DOM Elements|Todo List DOM Elements]]
- [[_COMMUNITY_Python Bot & Project Overview|Python Bot & Project Overview]]
- [[_COMMUNITY_Todo List Core Logic|Todo List Core Logic]]
- [[_COMMUNITY_OpenCode Configuration|OpenCode Configuration]]
- [[_COMMUNITY_Todo List Initialization|Todo List Initialization]]
- [[_COMMUNITY_Package Dependencies|Package Dependencies]]
- [[_COMMUNITY_Touch Gesture Handlers|Touch Gesture Handlers]]

## God Nodes (most connected - your core abstractions)
1. `main()` - 7 edges
2. `render()` - 7 edges
3. `init()` - 6 edges
4. `saveTasks()` - 4 edges
5. `addTask()` - 4 edges
6. `toggleTask()` - 4 edges
7. `deleteTask()` - 4 edges
8. `Verano 2026 Project Log` - 4 edges
9. `generate_html()` - 3 edges
10. `main()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `Verano 2026 Project Log` --references--> `init()`  [INFERRED]
  README.md → todolist/script.js
- `main()` --semantically_similar_to--> `main()`  [INFERRED] [semantically similar]
  pythonbot/bot.py → snakegame/snake.py
- `Verano 2026 Project Log` --references--> `main()`  [INFERRED]
  README.md → pythonbot/bot.py
- `Verano 2026 Project Log` --references--> `main()`  [INFERRED]
  README.md → snakegame/snake.py
- `Todo List HTML Page` --references--> `init()`  [INFERRED]
  todolist/index.html → todolist/script.js

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Swipe-to-Delete Interaction System** — todolist_script_handletouchstart, todolist_script_handletouchmove, todolist_script_handletouchend, todolist_script_closeotherswipes [EXTRACTED 1.00]
- **RSS-to-HTML News Pipeline** — pythonbot_bot_fetch_rss, pythonbot_bot_parse_rss, pythonbot_bot_generate_html, pythonbot_bot_card, pythonbot_bot_main [EXTRACTED 1.00]
- **Task CRUD Data Lifecycle** — todolist_script_loadtasks, todolist_script_savetasks, todolist_script_addtask, todolist_script_deletetask, todolist_script_toggletask, todolist_script_render [EXTRACTED 1.00]

## Communities (7 total, 2 thin omitted)

### Community 0 - "Todo List DOM Elements"
Cohesion: 0.14
Nodes (11): addBtn, dateEl, emptyState, emptySubtitle, emptyTitle, segments, swipeState, taskCount (+3 more)

### Community 1 - "Python Bot & Project Overview"
Cohesion: 0.31
Nodes (8): _card(), fetch_rss(), generate_html(), main(), parse_rss(), Gibraltar Culture News HTML, Verano 2026 Project Log, main()

### Community 2 - "Todo List Core Logic"
Cohesion: 0.24
Nodes (10): addTask(), deleteTask(), escapeHtml(), generateId(), getFilteredTasks(), handleDeleteClick(), handleTaskClick(), render() (+2 more)

### Community 3 - "OpenCode Configuration"
Cohesion: 0.40
Nodes (3): plugin, $schema, GraphifyPlugin()

### Community 4 - "Todo List Initialization"
Cohesion: 0.50
Nodes (4): Todo List HTML Page, init(), loadTasks(), updateDate()

## Knowledge Gaps
- **16 isolated node(s):** `$schema`, `plugin`, `@opencode-ai/plugin`, `tasks`, `taskList` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Verano 2026 Project Log` connect `Python Bot & Project Overview` to `OpenCode Configuration`, `Todo List Initialization`?**
  _High betweenness centrality (0.430) - this node is a cross-community bridge._
- **Why does `init()` connect `Todo List Initialization` to `Todo List DOM Elements`, `Python Bot & Project Overview`, `Todo List Core Logic`?**
  _High betweenness centrality (0.430) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `main()` (e.g. with `main()` and `Verano 2026 Project Log`) actually correct?**
  _`main()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `init()` (e.g. with `Verano 2026 Project Log` and `Todo List HTML Page`) actually correct?**
  _`init()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `@opencode-ai/plugin` to the rest of the system?**
  _16 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Todo List DOM Elements` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._