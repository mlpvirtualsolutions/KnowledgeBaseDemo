import { createClient } from "@/lib/supabase/server";
import { NextResponse, type NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get("code");

  if (code) {
    const supabase = createClient();
    await supabase.auth.exchangeCodeForSession(code);
    return NextResponse.redirect(new URL("/reset-password", request.url));
  }

  // No code — something went wrong with the link
  return NextResponse.redirect(new URL("/login", request.url));
}
