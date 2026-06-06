import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

const ALLOWED_PREFIXES = ['/_next', '/api', '/favicon.ico', '/assets'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname === '/' || ALLOWED_PREFIXES.some((prefix) => pathname.startsWith(prefix))) {
    return NextResponse.next();
  }

  const url = request.nextUrl.clone();
  url.pathname = '/';
  url.searchParams.set('from', pathname);
  return NextResponse.redirect(url);
}

export const config = {
  matcher: '/:path*',
};

