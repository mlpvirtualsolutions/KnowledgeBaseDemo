import { createClient } from "@supabase/supabase-js";

// Service-role client — bypasses RLS. Server-side only, never imported in
// client components or passed to the browser.
export function createAdminClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    { auth: { persistSession: false } }
  );
}
