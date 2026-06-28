import { jwtVerify } from "jose";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PROTECTED_PREFIXES = ["/dashboard", "/auctions/create"];
const EDIT_PATTERN = /^\/auctions\/[^/]+\/edit$/;

function isProtected(pathname: string): boolean {
  if (PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix))) return true;
  return EDIT_PATTERN.test(pathname);
}

async function hasValidAccessToken(token: string | undefined): Promise<boolean> {
  if (!token) return false;
  const secret = process.env.JWT_SIGNING_KEY;
  if (!secret) return false;
  try {
    // Verifying the signature server-side is all middleware needs to do —
    // httpOnly only blocks *client-side JS* from reading the cookie, it
    // doesn't stop this server-side check from reading and verifying it.
    await jwtVerify(token, new TextEncoder().encode(secret), { algorithms: ["HS256"] });
    return true;
  } catch {
    return false;
  }
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (!isProtected(pathname)) return NextResponse.next();

  const token = request.cookies.get("access_token")?.value;
  if (await hasValidAccessToken(token)) return NextResponse.next();

  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("next", pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/dashboard/:path*", "/auctions/create", "/auctions/:id/edit"],
};
