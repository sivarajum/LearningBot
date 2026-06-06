import { NextRequest, NextResponse } from 'next/server';

import { getContentTree, getMarkdownContent } from '@/lib/content-tree';
import type { TreeNode } from '@/lib/types';

export type SearchMatch = {
  path: string;
  name: string;
  breadcrumbs: string;
  matchType: 'filename' | 'heading' | 'content';
  matchText: string;
};

// ---------------------------------------------------------------------------
// In-memory search index with 5-minute TTL (mirrors content-tree.ts pattern)
// ---------------------------------------------------------------------------

type IndexEntry = {
  path: string;
  name: string;
  breadcrumbs: string;
  headings: string[];
  contentPreview: string; // first 500 chars of raw markdown
};

type IndexCache = {
  expiresAt: number;
  entries: IndexEntry[];
};

const CACHE_TTL_MS = 1000 * 60 * 5; // 5 minutes

const searchIndex: IndexCache = {
  expiresAt: 0,
  entries: [],
};

/** Collect all file paths from the tree. */
function collectFiles(nodes: TreeNode[]): { path: string; name: string }[] {
  const result: { path: string; name: string }[] = [];
  const walk = (items: TreeNode[]) => {
    for (const item of items) {
      if (item.type === 'file') {
        result.push({ path: item.path, name: item.name });
      } else if (item.children) {
        walk(item.children);
      }
    }
  };
  walk(nodes);
  return result;
}

/** Extract h1-h3 headings from raw markdown. */
function extractHeadings(content: string): string[] {
  const headings: string[] = [];
  const regex = /^#{1,3}\s+(.+)$/gm;
  let match: RegExpExecArray | null;
  while ((match = regex.exec(content)) !== null) {
    headings.push(match[1].trim());
  }
  return headings;
}

/** Build (or return cached) search index. */
async function getSearchIndex(): Promise<IndexEntry[]> {
  if (searchIndex.expiresAt > Date.now()) {
    return searchIndex.entries;
  }

  const tree = await getContentTree();
  const files = collectFiles(tree);
  const entries: IndexEntry[] = [];

  for (const file of files) {
    const breadcrumbs = file.path.replace(/\//g, ' / ');
    let headings: string[] = [];
    let contentPreview = '';

    try {
      const payload = await getMarkdownContent(file.path);
      headings = extractHeadings(payload.content);
      contentPreview = payload.content.slice(0, 500);
    } catch {
      // skip files that cannot be read
    }

    entries.push({
      path: file.path,
      name: file.name,
      breadcrumbs,
      headings,
      contentPreview,
    });
  }

  searchIndex.entries = entries;
  searchIndex.expiresAt = Date.now() + CACHE_TTL_MS;

  return entries;
}

/** Simple fuzzy-ish match: checks if all query words appear in the target. */
function fuzzyMatch(target: string, queryWords: string[]): boolean {
  const lower = target.toLowerCase();
  return queryWords.every((w) => lower.includes(w));
}

export async function GET(request: NextRequest) {
  const q = request.nextUrl.searchParams.get('q')?.trim();
  const limitParam = request.nextUrl.searchParams.get('limit');
  const limit = Math.min(Math.max(parseInt(limitParam ?? '20', 10) || 20, 1), 50);

  if (!q) {
    return NextResponse.json({ results: [] });
  }

  try {
    const entries = await getSearchIndex();
    const queryWords = q.toLowerCase().split(/\s+/).filter(Boolean);

    const results: SearchMatch[] = [];

    // Pass 1 — filename matches (highest priority)
    for (const entry of entries) {
      if (results.length >= limit) break;
      if (fuzzyMatch(entry.name, queryWords)) {
        results.push({
          path: entry.path,
          name: entry.name,
          breadcrumbs: entry.breadcrumbs,
          matchType: 'filename',
          matchText: entry.name,
        });
      }
    }

    // Pass 2 — heading matches
    if (results.length < limit) {
      const alreadyMatched = new Set(results.map((r) => r.path));
      for (const entry of entries) {
        if (results.length >= limit) break;
        if (alreadyMatched.has(entry.path)) continue;

        const matchedHeading = entry.headings.find((h) => fuzzyMatch(h, queryWords));
        if (matchedHeading) {
          results.push({
            path: entry.path,
            name: entry.name,
            breadcrumbs: entry.breadcrumbs,
            matchType: 'heading',
            matchText: matchedHeading,
          });
        }
      }
    }

    // Pass 3 — content matches
    if (results.length < limit) {
      const alreadyMatched = new Set(results.map((r) => r.path));
      for (const entry of entries) {
        if (results.length >= limit) break;
        if (alreadyMatched.has(entry.path)) continue;

        if (fuzzyMatch(entry.contentPreview, queryWords)) {
          const lowerContent = entry.contentPreview.toLowerCase();
          const idx = lowerContent.indexOf(queryWords[0]);
          const start = Math.max(0, idx - 40);
          const end = Math.min(entry.contentPreview.length, idx + 80);
          const snippet =
            (start > 0 ? '...' : '') +
            entry.contentPreview.slice(start, end).replace(/\n/g, ' ').trim() +
            (end < entry.contentPreview.length ? '...' : '');

          results.push({
            path: entry.path,
            name: entry.name,
            breadcrumbs: entry.breadcrumbs,
            matchType: 'content',
            matchText: snippet,
          });
        }
      }
    }

    return NextResponse.json({ results });
  } catch {
    return NextResponse.json(
      { error: 'Search failed' },
      { status: 500 },
    );
  }
}
