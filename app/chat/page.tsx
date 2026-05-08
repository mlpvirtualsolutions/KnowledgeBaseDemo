import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { createAdminClient } from "@/lib/supabase/admin";
import Navbar from "@/components/Navbar";
import ChatClient from "@/components/ChatClient";

export default async function ChatPage() {
  const supabase = createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) redirect("/login");

  const admin = createAdminClient();

  const { data: profile } = await admin
    .from("users")
    .select("company_id")
    .eq("id", user.id)
    .single();

  let companyName = "YOUR";
  if (profile?.company_id) {
    const { data: company } = await admin
      .from("companies")
      .select("name")
      .eq("id", profile.company_id)
      .single();
    if (company?.name) {
      companyName = (company.name as string).toUpperCase();
    }
  }

  return (
    <div className="min-h-screen bg-logidex-bg">
      <Navbar userEmail={user.email ?? ""} />
      <ChatClient companyName={companyName} />
    </div>
  );
}
