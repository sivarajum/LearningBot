export type TreeNode = {
  name: string;
  path: string;
  type: 'folder' | 'file';
  children?: TreeNode[];
};

export type MarkdownPayload = {
  path: string;
  name: string;
  content: string;
  breadcrumbs: { label: string; path: string }[];
};

