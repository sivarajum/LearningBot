## LearningBot Explorer

World-class reading experience for the local `LearningBot` knowledge base. Browse every Markdown file inside the repository with instant previews, Mermaid diagrams, syntax highlighting, and a persistent two-pane layout.

### Highlights

- 🔍 Real-time folder tree explorer with filtering and refresh
- 🧭 Breadcrumbs + back/home navigation without leaving the main page
- 🧠 Markdown rendered with GitHub-flavored tables, inline HTML, and code highlighting
- 🧾 Mermaid diagrams rendered inline via client-side `mermaid`
- 🎨 Tailwind CSS-driven UI with responsive, glassy layout and typography polish
- 🔐 Local-only filesystem access guarded by path sanitization

### Prerequisites

- Node.js 18.18+ (Next.js 16 requirement)
- npm (bundled with Node)

### Configure the Markdown root (optional)

By default the app indexes the parent directory of this project (i.e., the whole `LearningBot` repo).  
To override, set `MARKDOWN_ROOT` in `.env.local`:

```bash
echo "MARKDOWN_ROOT=/absolute/path/to/your/content" > .env.local
```

> The renderer only serves `.md`, `.markdown`, and `.mdx` files. Directories such as `.git`, `node_modules`, `.next`, and `learning-viewer` are automatically excluded.

### Install & run

```bash
npm install
npm run dev
```

Navigate to [http://localhost:3000](http://localhost:3000) — the entire experience lives on that single page. Use the sidebar to pick any file; the right pane updates instantly without a page navigation.

### Quality checks

```bash
npm run lint   # ESLint (Next.js defaults + TypeScript)
npm run build  # Production build / type-check
```

### Project structure

- `src/lib/content-tree.ts` — filesystem crawler + markdown loader (with caching & path guards)
- `src/app/api/*` — API routes for tree + markdown payloads
- `src/components/Explorer.tsx` — main UX: sidebar, content area, breadcrumbs
- `src/components/MarkdownRenderer.tsx` — React Markdown + syntax highlighting + Mermaid bridge
- `middleware.ts` — redirects any stray route back to `/` to keep the SPA-like feel

### Tech stack

- Next.js 16 (App Router, Server Components + Client Islands)
- Tailwind CSS + Tailwind Typography
- React Markdown, Remark GFM, Rehype Raw
- Mermaid, React Syntax Highlighter, SWR, Lucide icons
