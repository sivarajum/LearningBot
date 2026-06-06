import { NextRequest, NextResponse } from 'next/server';

import { getMarkdownContent } from '@/lib/content-tree';

export async function GET(request: NextRequest) {
  const path = request.nextUrl.searchParams.get('path');

  if (!path) {
    return NextResponse.json({ error: 'Missing `path` query param' }, { status: 400 });
  }

  try {
    const payload = await getMarkdownContent(path);
    return NextResponse.json(payload);
  } catch (error) {
    return NextResponse.json(
      { error: (error as Error).message },
      { status: 400 },
    );
  }
}

