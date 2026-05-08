import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";

export async function GET() {
  // Verify session
  const supabase = createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  // Confirm super_admin role
  const admin = createAdminClient();
  const { data: profile } = await admin
    .from("users")
    .select("role")
    .eq("id", user.id)
    .single();

  if (profile?.role !== "super_admin") {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  // Return all companies — id and name only, never webhook URLs
  const { data: companies, error } = await admin
    .from("companies")
    .select("id, name")
    .order("name", { ascending: true });

  if (error) {
    return NextResponse.json({ error: "Failed to fetch companies" }, { status: 500 });
  }

  return NextResponse.json(companies);
}
