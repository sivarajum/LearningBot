# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**LearningBot** is a personal learning and portfolio repository covering ML, AI, data engineering, cloud platforms, and career development. It contains:

- **Numbered learning modules** (`01-ML-Fundamentals` through `14-TechStack`) — markdown-based study guides, each with its own README
- **Sj-Prod/** — Production-grade systems (Python + Docker). See `Sj-Prod/CLAUDE.md` for detailed guidance
- **learning-viewer/** — Next.js 16 app (React 19, TypeScript, Tailwind) for browsing learning content
- **4k_cheatsheets/** — Generated 4K PNG cheat sheets (3840x2160, 300 DPI)
- **Frontend/** — TypeScript learning guides
- **todo/** — Planning docs and reference materials

## Common Commands

### Learning Viewer (Next.js)

```bash
./start.sh                          # install deps + start dev server on :3000
# or manually:
cd learning-viewer && npm install && npm run dev
npm run build                       # production build
npm run lint                        # ESLint
```

### 4K Cheat Sheet Generation

```bash
python generate_all_4k_cheatsheets.py       # all 17 sheets
python generate_4k_cheatsheets.py           # core modules (5)
python generate_4k_cheatsheets_extended.py  # advanced (6)
python generate_4k_techstack.py             # tech stack (6)
```

Output goes to `4k_cheatsheets/` (PNGs are gitignored).

### Sj-Prod Systems

Each system is independent. Enter the system directory and follow its pattern:

```bash
cd Sj-Prod/<System-Name>
pip install -r requirements.txt
python main.py [api|ui|all|pipeline|validate|simulate]
```

Linting across all systems: `ruff check Sj-Prod/` (shared config at `Sj-Prod/ruff.toml`).

See `Sj-Prod/CLAUDE.md` for per-system details including testing.

## Architecture Notes

- The numbered modules (01-14) are **content-only** (markdown, diagrams). No code to build or test.
- `learning-viewer/` reads the numbered module markdown files and renders them as a web app.
- `Sj-Prod/` is the area with runnable Python production systems, tests, Docker, and APIs. It has its own CLAUDE.md with full details.
- The `generate_*_cheatsheets*.py` scripts at the root produce matplotlib-rendered PNG images.
- `.gitignore` excludes `.venv/`, `node_modules/`, `.env`, `*.joblib`, `*.pkl`, `*.parquet`, `*.duckdb`, and `4k_cheatsheets/*.png`.
