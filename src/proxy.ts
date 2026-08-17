import { NextRequest, NextResponse } from "next/server";

/**
 * QalaJob AI — Route protection middleware.
 * Checks for access token and redirects unauthenticated users.
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Protected routes that require authentication
  const protectedPaths = [
    "/dashboard",
  ];

  const isProtected = protectedPaths.some((p) => pathname.startsWith(p));

  // Check for auth flag in cookie (set by session.ts on login)
  const token = request.cookies.get("qalajob-auth")?.value;

  // Role from cookie (set by session.ts during login)
  const role = request.cookies.get("qalajob-role")?.value;

  if (isProtected && !token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Role-based dashboard access
  if (pathname.startsWith("/dashboard/admin") && role && role !== "admin") {
    return NextResponse.redirect(new URL(`/dashboard/${role}`, request.url));
  }

  if (pathname.startsWith("/dashboard/employer") && role && role !== "employer" && role !== "admin") {
    return NextResponse.redirect(new URL(`/dashboard/${role}`, request.url));
  }

  if (pathname.startsWith("/dashboard/student") && role && role !== "student" && role !== "admin") {
    return NextResponse.redirect(new URL(`/dashboard/${role}`, request.url));
  }

  // Security headers for all responses
  const response = NextResponse.next();
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-XSS-Protection", "1; mode=block");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  response.headers.set(
    "Permissions-Policy",
    "camera=(), microphone=(), geolocation=()"
  );

  return response;
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/login",
  ],
};
