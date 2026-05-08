import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  // Supabase SSR requires this specific pattern — do not add logic between
  // createServerClient and getUser() or sessions may randomly break.
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet: { name: string; value: string; options: CookieOptions }[]) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const path = request.nextUrl.pathname;

  // No session — let /login through, block everything else
  if (!user) {
    if (path === "/login") return supabaseResponse;
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Authenticated — fetch role (RLS policy allows users to read their own row)
  const { data: profile, error: profileError } = await supabase
    .from("users")
    .select("role")
    .eq("id", user.id)
    .single();

  console.log("[middleware] user.id:", user.id);
  console.log("[middleware] profile:", profile);
  console.log("[middleware] profileError:", profileError);

  const role = profile?.role as string | undefined;

  // Redirect authenticated users away from /login to their home page
  if (path === "/login") {
    if (role === "super_admin")   return NextResponse.redirect(new URL("/superadmin",   request.url));
    if (role === "company_admin") return NextResponse.redirect(new URL("/admin/users",  request.url));
    return NextResponse.redirect(new URL("/chat", request.url));
  }

  // Redirect super_admin away from /chat to their home page
  if (path === "/chat" && role === "super_admin") {
    return NextResponse.redirect(new URL("/superadmin", request.url));
  }

  // Role-based access control for protected routes
  if (path.startsWith("/superadmin") && role !== "super_admin") {
    return NextResponse.redirect(new URL("/chat", request.url));
  }

  if (path.startsWith("/admin") && role !== "company_admin" && role !== "super_admin") {
    return NextResponse.redirect(new URL("/chat", request.url));
  }

  return supabaseResponse;
}

export const config = {
  matcher: ["/login", "/chat", "/admin/:path*", "/superadmin", "/reset-password"],
};
