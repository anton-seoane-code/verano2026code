# Report
## 01/07
### Projects:
- [ ] Nannoid `nannoid/`
  - Breakout clone with space graphics by Phil Hassey (2005), recreated from original source
  - 24 levels, tile-based rendering (32×16), 640×480 resolution
  - Full game mechanics: ball physics, paddle types, 6 power-up pills, lasers, floating junk enemies
  - All original sprite images, sound effects, and level files
  - Modern pygame 2.x codebase with modular architecture (engine/game/screens)
  - High score persistence via pickle
  - Controls: mouse + keyboard, normal and "sissy" modes
  - Dependencies: pygame
- [x] Snake 2006 `snake-2006/`
  - Classic Snake recreation by Cifa (pygame.org/project/433) from scratch
  - Grid-based movement (30x30) on a 600x600 board
  - Red food: +1 point, permanent until eaten
  - Blue bonuses: +5 points, spawn briefly and blink before disappearing
  - Pause with 'P' key and overlay
  - High score persistence to local file (`snake_2006.high`)
  - Start screen with instructions, game over with new high score detection
  - All graphics rendered with `pygame.draw` primitives (original source links were dead)
  - Controls: Arrow keys to move
  - Dependencies: pygame
- [x] Space Invaders — Alien Conquer `space-invaders/`
  - Full recreation of Alien Conquer by Taiua Pires (pygame.org/project/584) from scratch
  - 1–4 player arcade space shooter with 4 color-coded ships (Red, Green, Blue, Yellow)
  - AI opponent with targeting and dodging behavior
  - Aliens switch color on hit; scoring: +10 same color, +20 different color
  - Resurrection mechanic: leading player revives instead of dying
  - Power-ups: blue laser cannon (rapid piercing shots) and red bullet time (slow motion)
  - Ship-to-ship collision detection
  - JSON config save/load (`alien_conquer.cfg`)
  - Credits screen with auto-scrolling and speed control
  - How to Play screen with full controls, scoring rules, power-up legend
  - Title screen, game-over screen, configuration screen, HUD with scores and lives
  - 4 keyboard control schemes (arrows+RCTRL, WASD+SPACE, JIKL+P, numpad) + joystick auto-detect
  - All graphics rendered with `pygame.draw` primitives (original source links were dead)
  - Ship triangle now points in direction of movement; bullets fire from tip
  - Dependencies: pygame

## 26/06
### Projects:
- [x] Study Assistant `study-assistant/`
  - CLI + Web GUI tool: scans directories with `.txt`/`.pdf` files, generates three output types:
    - **Summaries** — extractive summarization via sentence scoring (frequency + position + length)
    - **Mind maps** — Markmap-format interactive mind maps from keyword extraction & topic clustering
    - **Quizzes** — multiple-choice questions (a/b/c) with distractors from source text
  - Web GUI (`python server.py`): dark glassmorphism UI, scan dir → file selection → generate → results
    - Markdown summary rendering, markmap.js mind map rendering, interactive quiz with reveal-answer
  - REST API: `POST /api/scan` lists files, `POST /api/generate` produces summaries/mindmaps/quizzes
    - `POST /api/export/pdf` converts markdown to PDF download
    - `GET /api/history` / `GET /api/history/<id>` — browse and restore past sessions
    - `POST /api/history/clear` — delete all history
  - CLI: `python main.py --dir <path> --all` (or `--summaries`/`--mindmaps`/`--quizzes`)
  - Core modules: `reader.py` (txt + PDF via PyMuPDF), `summarizer.py` (extractive), `mindmap_gen.py` (keyword clustering), `quiz_gen.py` (term blanking + distractor selection)
  - Sample files in `samples/` for quick testing
  - Dependencies: PyMuPDF

## 25/06
### Projects:
- [x] Simple Games `simple-games/`
  - SPA con HTML/CSS/JS: interfaz gráfica en navegador, mismo diseño glassmorphism oscuro que `todolist/`
  - Tic-Tac-Toe: grid 3×3 clickeable, PvP y 3 niveles de IA (Minimax con poda alfa-beta), selector de dificultad
  - Hangman: Canvas con dibujo del ahorcado (6 etapas), teclado QWERTY interactivo, palabras embebidas
  - Rock-Paper-Scissors: 3 botones con emoji, al mejor de 3 rondas contra la máquina
  - Scoreboard persistente en `localStorage` con filtro por juego y tabla de resultados
  - Sin servidor necesario: abrir `index.html` en cualquier navegador
- [x] Simple Games (Hermes Edition) `simple-games-hermes/`
  - SPA completa con HTML/CSS/JS: misma base visual glassmorphism oscuro con mejoras
  - Tic-Tac-Toe: IA con Minimax + poda alfa-beta, animación pop-in en celdas, sonido, confeti al ganar, resaltado de línea ganadora
  - Hangman: 4 categorías temáticas (Programming, Animals, Food, Mixed) con pista, Canvas mejorado con ojos en la figura, entrada por teclado físico QWERTY
  - Rock-Paper-Scissors: 2 variantes (Classic y Lizard-Spock con 5 opciones), cada opción con emoji propio, sonido por ronda
  - Stats panel: tarjetas de Wins/Losses/Draws totales + tabla por juego con racha activa y racha máxima 🔥
  - Sound engine: efectos de sonido vía Web Audio API (sin archivos externos) — click, place, win, lose, draw, correct, wrong
  - Confetti: animación CSS particle al ganar cualquier juego
  - Scoreboard: persistente en `localStorage`, filtro por juego, mismo diseño que la versión original
  - Keyboard shortcuts: teclas 1-4 para navegar entre pestañas, teclas A-Z para Hangman
  - Sin servidor necesario: abrir `index.html` en cualquier navegador

### Code Review — Simple Games vs Simple Games Hermes

#### Errors in `simple-games/`:

| # | File | Error |
|---|------|-------|
| 1 | `style.css` | `var(--radius-lg)` used but never defined in `:root` — broken border-radius on `.game-btn` |
| 2 | `app.js` | TTT win highlight marks all filled cells of both players instead of only the 3 winning cells |
| 3 | `index.html` | Hangman has no category selection or hint system — 42 flat words with no theming |
| 4 | `app.js` | RPS locked to Classic variant only, no Lizard-Spock support |
| 5 | `app.js` | No keyboard shortcuts for tab navigation or Hangman letter input |
| 6 | `style.css` | No responsive media queries — layout breaks on narrow viewports |
| 7 | `app.js` | No sound effects or visual celebrations (confetti, animations) on game events |

#### Errors in `simple-games-hermes/`:

None identified — all original bugs are fixed and no new issues introduced.

#### Improvements Hermes introduces over the original:
- Sound engine: 7 distinct sound effects via Web Audio API (click, place, win, lose, draw, correct, wrong)
- Confetti: CSS particle animation celebration on any game win
- Keyboard shortcuts: keys 1-4 for tab navigation, keys A-Z for Hangman letter input
- Hangman categories: 4 thematic word pools (Programming, Animals, Food, Mixed) with 80 total words and per-category hints
- RPS Lizard-Spock variant: 5-choice mode switchable via selector, each option with emoji
- Stats dashboard: win/loss/draw counters, per-game breakdowns, active streak and max streak tracking
- Pop-in animation on TTT cell placement, pulse effect on winning cells, precise win-line highlighting (only 3 cells)
- Hangman canvas: added rope line above head and eyes on the figure
- RPS variant saved in score entries for detailed history
- CSS bug fix: `var(--radius-lg)` corrected to `var(--radius)`
- Responsive design: `@media (max-width: 420px)` breakpoint
- Separate `localStorage` key (`simple-games-hermes-scores`) to avoid score collision with original

## 23/06
### Projects:
- [x] Directory Analyzer `directory-analyzer/`
  - CLI que analiza un directorio, clasifica archivos por tipo (imágenes, vídeos, documentos) y los organiza en subdirectorios automáticamente
  - Flags: `--dry-run`, `--copy`, `--recursive`
  - Web GUI con tree browser, detección de duplicados (SHA256) e informe detallado
  - API JSON
  - Dependencias: solo stdlib
 - [x] Directory Analyzer (Hermes Edition) `directory-analyzer-hermes/`
  - CLI con auto-clasificación en imágenes, vídeos y documentos con subdirectorios con emojis (📷 🎬 📄)
  - Flags: `--dry-run`, `--copy`, `--recursive`, `--detect-duplicates`, `--analyze-only`
  - Web GUI con file browser integrado, detección de duplicados por SHA256, y organize preview
  - API JSON endpoints: browse, analyze, organize
  - Dependencias: solo stdlib

### Code Review — Directory Analyzer vs Directory Analyzer Hermes

#### Errors in `directory-analyzer/`:

| # | File | Error |
|---|------|-------|
| 1 | `analyzer.py:37,40-41` | **`--recursive` flag is non-functional** — `rglob('*')` finds files recursively but `is_in_subdirectory()` immediately skips all files in subdirectories (`len(relative.parts) > 1`). The flag has zero effect. |
| 2 | `analyzer.py:25` | **No `ValueError` handling in `is_in_subdirectory`** — `relative_to()` raises `ValueError` if `filepath` is not under `root`, which would crash the scan. |
| 3 | `server.py:179` | **`format` parameter shadows built-in** — `log_message(self, format, *args)` shadows Python's `format()` built-in. |
| 4 | `analyzer.py:170-171` | **Exits with code 0 on error** — `main()` prints the error and returns (exit 0) instead of `sys.exit(1)`. |
| 5 | `analyzer.py:170` | **Error messages go to stdout** — `print(f'Error: {e}')` should use `file=sys.stderr`. |
| 6 | `server.py:3-4` | **Unused imports** — `mimetypes` and `os` imported but never used. |
| 7 | `server.py:104` | **`handle_browse` returns dirs as raw strings** — `[str(d) for d in dirs]` instead of dicts with `name`/`path` keys, limiting frontend display. |
| 8 | `server.py:141-145` | **Response missing `category_counts`, `unrecognized_count`, `category_dirs`** — frontend must recompute these from raw lists. |

#### Errors in `directory-analyzer-hermes/`:

| # | File | Error |
|---|------|-------|
| 1 | `analyzer.py:59-60,63-64` | **Same `--recursive` bug** — `glob('**/*')` finds files recursively but `is_in_subdirectory()` skips them all. Same root cause as original. |
| 2 | `server.py:66` | **`do_POST` doesn't parse URL path** — uses `self.path` directly instead of `urlparse(self.path).path`. Query params in POST URLs (e.g. `/api/analyze?foo=bar`) would break routing returning 404. |
| 3 | `server.py:7` | **Unused import** — `import re` is never used. |

#### Fixes Hermes introduces over the original:
- Catches `ValueError` in `is_in_subdirectory` (fixes error #2 of original)
- Uses `sys.exit(1)` on scan errors (fixes error #4)
- Routes error messages to `stderr` (fixes error #5)
- Uses `_format` instead of `format` to avoid shadowing built-in (fixes error #3)
- Richer API responses: `category_counts`, `unrecognized_count`, `category_dirs`, `created_directories`
- Adds `CATEGORY_DIRS` mapping with emoji subdirectory names
- Includes epilog with usage examples in CLI help
## 22/06
### Projects:
- [x] API Definition Document `api-definicion/`
  - Definición de API con analogía del restaurante
  - Componentes clave, tipos (REST, GraphQL, SOAP, WebSocket, gRPC) y ejemplo conceptual
- [x] GitHub Repo Searcher `repo-searcher/`
  - CLI con búsqueda por palabra clave, lenguaje (`--language`) y estrellas mínimas (`--min-stars`)
  - GUI con tkinter (campos de filtro, tabla de resultados, búsqueda en hilo separado)
  - Dependencias: `requests` + `rich`
## 19/06
### Projects:
- [x] PDF Exam Generator (made with OpenCode)
  - Difficulty levels: easy, mid, hard (`-d` flag)
  - Configurable question count (`-q` flag)
- [x] PDF Exam Generator Hermes `pdf-exam-hermes/`
  - Built with Hermes Agent (interactive CLI)
  - Difficulty levels: easy, mid, hard (`-d` flag)
  - Configurable question count (`-q` flag, default: 10)
  - Results screen with pass/fail per question
## 18/06
### Projects:
- [x] Installed Graphify on OpenCode
- [x] Processing Sketches (particles, waves, fractal tree, boids, morph, interactive)
## 16/06
### Projects: 
- [x] Opencode and Hermes installed on Hyper-V

## 15/06
### Projects: 
- [x] Python Snake Game
## 08/06
### Projects: 
- [x] To-Do List
- [x] Python Gibraltarian Bot

