# Prompt for Cursor Agent: Personal Static Knowledge Platform

## Project Overview
Create a basic, no-login, easy-to-read personal knowledge base site using static HTML, CSS, and optionally simple JavaScript. The platform should help you organize and read your own content frequently and efficiently, with zero authentication, no security, and a clear folder structure. No backend or database; all content as files.

## Tech Stack
- HTML (pages)
- CSS (site-wide styles)
- JavaScript (optional for search/navigation/filtering)
- Static site generator (recommended: Eleventy or Hugo)

---

## Requirements
1. **No authentication** or login anywhere
2. **Static-only** site — generated files only, no server/database/API
3. **Easy file organization** — clear folder structure with obvious names
4. **Quick navigation** — top-level menu, sidebar or search, always visible
5. **Simple Markdown/HTML content** — each note/lesson as one file
6. **Offline access** — PWA optional, download site for reading anytime
7. **Global styles** for maximum clarity and legibility
8. **Minimal JavaScript** — only if really needed for search/filter/sorting

## Starter Folder Structure
```
/content        # Markdown/HTML lessons, notes
/pages          # Important HTML pages (index, about, topics)
/assets         # Images, PDFs, videos
/styles         # CSS files
/scripts        # JavaScript files (optional)
```

## Templates & Defaults
- **index.html** — Home page with site menu, summary of all topics
- **topic.html** — Topics/sections menu (auto-generated if SSG)
- **lesson.html** — Each lesson page uses same layout: title, content, links, next/prev buttons
- **Global header/footer** — Consistent, shows site name and main menu

## Optional Extras
- Site-wide search (simple JS or by SSG)
- Offline support (add manifest.json + basic service worker)
- Print-friendly CSS for all pages

## Build & Usage Steps
1. **Write notes/lessons** in Markdown or HTML files, save in /content
2. **Run SSG** (Eleventy or Hugo) or manually duplicate HTML for each page
3. **Open site locally or host on any static server** (GitHub Pages, Netlify, Vercel, etc.)

## Examples
- "Generate index.html listing all lessons in /content. Each lesson shows title, link, and summary."
- "Create a simple navigation menu with links to topic.html, about.html, settings.html, and all lessons."
- "For lesson.html, use big title heading, content section, next/previous page links, and optional download button."
- "Add print-friendly CSS — when printed, show only page content as simple black text."
- "Make the site installable as a PWA. Add manifest.json and a basic offline service worker for static assets."

## Clarity Rules
- Every page uses the same header/footer
- All lessons follow same layout, so reading is easy and consistent
- No confusion: All notes are flat files, easy to open and find
- Never use authentication, permissions, or hidden sections
- No unnecessary code complexity

---

**END OF PROMPT**
