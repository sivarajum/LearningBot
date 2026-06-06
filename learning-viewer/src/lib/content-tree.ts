import fs from 'fs';
import path from 'path';

import type { MarkdownPayload, TreeNode } from './types';

const IGNORED_DIRECTORIES = new Set([
  '.git',
  '.github',
  '.idea',
  '.vscode',
  'node_modules',
  'learning-viewer',
  'learning-viewer/node_modules',
  'learning-viewer/.next',
  '.next',
  '.turbo',
  'dist',
  'build',
]);

const MARKDOWN_EXTENSIONS = new Set(['.md', '.markdown', '.mdx']);

const CACHE_TTL_MS = 1000 * 60 * 5;

const markdownRoot =
  process.env.MARKDOWN_ROOT ?? path.resolve(process.cwd(), '..');

type CacheEntry = {
  expiresAt: number;
  data: TreeNode[];
};

const treeCache: CacheEntry = {
  expiresAt: 0,
  data: [],
};

function isMarkdownFile(filePath: string) {
  return MARKDOWN_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

function shouldIgnore(entryPath: string) {
  const segments = entryPath.replace(/\\/g, '/').split('/');
  return segments.some((seg) => IGNORED_DIRECTORIES.has(seg));
}

function buildTree(dirPath: string, relativePath = ''): TreeNode[] {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });

  const nodes: TreeNode[] = [];

  for (const entry of entries) {
    if (entry.name.startsWith('.')) continue;

    const absolutePath = path.join(dirPath, entry.name);
    const entryRelativePath = path.join(relativePath, entry.name);

    if (shouldIgnore(entryRelativePath)) continue;

    if (entry.isDirectory()) {
      const children = buildTree(absolutePath, entryRelativePath);
      if (children.length > 0) {
        nodes.push({
          name: entry.name,
          path: entryRelativePath,
          type: 'folder',
          children,
        });
      }
    } else if (entry.isFile() && isMarkdownFile(entry.name)) {
      nodes.push({
        name: entry.name,
        path: entryRelativePath,
        type: 'file',
      });
    }
  }

  return nodes.sort((a, b) => {
    if (a.type === b.type) {
      return a.name.localeCompare(b.name);
    }
    return a.type === 'folder' ? -1 : 1;
  });
}

export async function getContentTree(force = false): Promise<TreeNode[]> {
  if (!force && treeCache.expiresAt > Date.now()) {
    return treeCache.data;
  }

  const tree = buildTree(markdownRoot);
  treeCache.data = tree;
  treeCache.expiresAt = Date.now() + CACHE_TTL_MS;

  return tree;
}

function sanitizeRelativePath(relativePath: string) {
  const normalized = path
    .normalize(relativePath)
    .replace(/^(\.\.(\/|\\|$))+/, '')
    .replace(/\\/g, '/');
  return normalized;
}

export async function getMarkdownContent(
  relativePath: string,
): Promise<MarkdownPayload> {
  const safeRelativePath = sanitizeRelativePath(relativePath);
  const absolutePath = path.join(markdownRoot, safeRelativePath);

  const resolvedRoot = path.resolve(markdownRoot) + path.sep;
  const resolvedPath = path.resolve(absolutePath);
  if (!resolvedPath.startsWith(resolvedRoot)) {
    throw new Error('Access denied.');
  }

  const exists = fs.existsSync(absolutePath);
  if (!exists) {
    throw new Error('File not found');
  }

  if (!isMarkdownFile(absolutePath)) {
    throw new Error('Only markdown files are supported');
  }

  const content = fs.readFileSync(absolutePath, 'utf-8');
  const breadcrumbs = buildBreadcrumbs(safeRelativePath);

  return {
    path: safeRelativePath,
    name: path.basename(safeRelativePath),
    content,
    breadcrumbs,
  };
}

function buildBreadcrumbs(relativePath: string) {
  const segments = relativePath.split('/').filter(Boolean);
  const breadcrumbs: { label: string; path: string }[] = [];

  segments.forEach((segment, index) => {
    const subPath = segments.slice(0, index + 1).join('/');
    breadcrumbs.push({
      label: segment.replace(/-/g, ' '),
      path: subPath,
    });
  });

  return breadcrumbs;
}

