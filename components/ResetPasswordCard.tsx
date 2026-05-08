"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

export default function ResetPasswordCard() {
  const router = useRouter();
  const [password, setPassword]   = useState("");
  const [confirm, setConfirm]     = useState("");
  const [error, setError]         = useState("");
  const [loading, setLoading]     = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!password || !confirm) {
      setError("Please fill in both fields.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);
    const supabase = createClient();

    const { data, error: updateError } = await supabase.auth.updateUser({
      password,
    });

    if (updateError || !data.user) {
      setError("Failed to update password. Your link may have expired.");
      setLoading(false);
      return;
    }

    // Route to correct home page based on role
    const { data: profile } = await supabase
      .from("users")
      .select("role")
      .eq("id", data.user.id)
      .single();

    const role = profile?.role as string | undefined;

    if (role === "super_admin") {
      router.push("/superadmin");
    } else if (role === "company_admin") {
      router.push("/admin/users");
    } else {
      router.push("/chat");
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-logidex-bg px-4">
      <div className="w-full max-w-[340px]">

        {/* Brand heading */}
        <div className="text-center mb-7">
          <div className="text-[2rem] font-extrabold tracking-[0.04em] text-logidex-navy">
            LOGI<span className="text-logidex-blue">DEX</span>
          </div>
          <div className="text-logidex-muted text-[0.875rem] mt-2">
            Set a new password
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="bg-white border border-logidex-border rounded-2xl px-6 pt-7 pb-5 shadow-[0_2px_12px_rgba(0,0,0,0.06)]">
            <div className="flex flex-col gap-4">

              {error && (
                <div className="text-[0.82rem] text-red-500 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                  {error}
                </div>
              )}

              <div className="flex flex-col gap-[6px]">
                <label className="text-[0.82rem] font-medium text-logidex-text-dark">
                  New password
                </label>
                <input
                  type="password"
                  placeholder="At least 8 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full border border-logidex-border rounded-[10px] bg-slate-50 text-[0.88rem] text-logidex-text-dark px-[14px] py-[10px] outline-none transition-all duration-150 focus:border-logidex-blue focus:bg-white focus:ring focus:ring-logidex-blue/[.12] focus:ring-offset-0"
                />
              </div>

              <div className="flex flex-col gap-[6px]">
                <label className="text-[0.82rem] font-medium text-logidex-text-dark">
                  Confirm password
                </label>
                <input
                  type="password"
                  placeholder="Repeat your new password"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  className="w-full border border-logidex-border rounded-[10px] bg-slate-50 text-[0.88rem] text-logidex-text-dark px-[14px] py-[10px] outline-none transition-all duration-150 focus:border-logidex-blue focus:bg-white focus:ring focus:ring-logidex-blue/[.12] focus:ring-offset-0"
                />
              </div>

              <div className="h-1" />

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-logidex-blue hover:bg-logidex-blue-hover disabled:opacity-60 text-white rounded-[10px] font-semibold text-[0.9rem] h-11 tracking-[0.01em] cursor-pointer transition-colors duration-150 border-none"
              >
                {loading ? "Saving…" : "Set new password"}
              </button>

            </div>
          </div>
        </form>

      </div>
    </div>
  );
}
