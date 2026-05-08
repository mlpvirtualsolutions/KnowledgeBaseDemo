"use client";

import { useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

export default function ForgotPasswordCard() {
  const [email, setEmail]     = useState("");
  const [error, setError]     = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent]       = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!email) {
      setError("Please enter your email address.");
      return;
    }

    setLoading(true);
    const supabase = createClient();

    const { error: resetError } = await supabase.auth.resetPasswordForEmail(
      email,
      {
        redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
      }
    );

    if (resetError) {
      setError("Something went wrong. Please try again.");
      setLoading(false);
      return;
    }

    setSent(true);
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
            Reset your password
          </div>
        </div>

        <div className="bg-white border border-logidex-border rounded-2xl px-6 pt-7 pb-5 shadow-[0_2px_12px_rgba(0,0,0,0.06)]">
          {sent ? (
            <div className="flex flex-col gap-4 text-center">
              <p className="text-[0.88rem] text-logidex-text leading-relaxed">
                Check your email — a reset link is on its way to{" "}
                <span className="font-medium text-logidex-navy">{email}</span>.
              </p>
              <p className="text-[0.8rem] text-logidex-muted">
                The link expires in 1 hour.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="flex flex-col gap-4">
                {error && (
                  <div className="text-[0.82rem] text-red-500 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                    {error}
                  </div>
                )}

                <div className="flex flex-col gap-[6px]">
                  <label className="text-[0.82rem] font-medium text-logidex-text-dark">
                    Email address
                  </label>
                  <input
                    type="email"
                    placeholder="you@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full border border-logidex-border rounded-[10px] bg-slate-50 text-[0.88rem] text-logidex-text-dark px-[14px] py-[10px] outline-none transition-all duration-150 focus:border-logidex-blue focus:bg-white focus:ring focus:ring-logidex-blue/[.12] focus:ring-offset-0"
                  />
                </div>

                <div className="h-1" />

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-logidex-blue hover:bg-logidex-blue-hover disabled:opacity-60 text-white rounded-[10px] font-semibold text-[0.9rem] h-11 tracking-[0.01em] cursor-pointer transition-colors duration-150 border-none"
                >
                  {loading ? "Sending…" : "Send reset link"}
                </button>
              </div>
            </form>
          )}
        </div>

        <div className="text-center mt-5">
          <Link
            href="/login"
            className="text-[0.82rem] text-logidex-muted hover:text-logidex-navy transition-colors duration-150"
          >
            ← Back to sign in
          </Link>
        </div>

      </div>
    </div>
  );
}
