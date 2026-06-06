import { NextRequest, NextResponse } from 'next/server';

import { getContentTree } from '@/lib/content-tree';

export async function GET(request: NextRequest) {
  try {
    const force = request.nextUrl.searchParams.get('refresh') === '1';
    const tree = await getContentTree(force);
    return NextResponse.json({ tree });
  } catch (error) {
    return NextResponse.json(
      { error: (error as Error).message },
      { status: 500 },
    );
  }
}

