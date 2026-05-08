"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { createClient } from "@/lib/supabase/client";

export default function LoginCard() {
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true);
    const supabase = createClient();

    const { data, error: authError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (authError || !data.user) {
      setError("Invalid email or password.");
      setLoading(false);
      return;
    }

    // Hard redirect so middleware sees the session cookie and routes by role
    window.location.href = "/";
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-logidex-bg px-4">
      <div className="w-full max-w-[340px]">

        {/* Logo */}
        <div className="flex justify-center mb-6">
          <Image
            src="/logidex-logo-new.png"
            alt="Logidex"
            width={340}
            height={89}
            quality={100}
            priority
          />
        </div>

        {/* Card */}
        <form onSubmit={handleSubmit}>
          <div className="bg-white border border-logidex-border rounded-2xl px-6 pt-6 pb-5 shadow-[0_2px_12px_rgba(0,0,0,0.06)]">
            <div className="flex flex-col gap-4">

              {/* Card heading */}
              <div className="mb-1">
                <h2 className="text-[1.15rem] font-bold text-logidex-navy leading-snug">
                  Welcome back
                </h2>
                <p className="text-[0.82rem] text-logidex-muted mt-[3px]">
                  Sign into your account
                </p>
              </div>

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

              <div className="flex flex-col gap-[6px]">
                <div className="flex items-center justify-between">
                  <label className="text-[0.82rem] font-medium text-logidex-text-dark">
                    Password
                  </label>
                  <Link
                    href="/forgot-password"
                    className="text-[0.78rem] text-logidex-muted hover:text-logidex-blue transition-colors duration-150"
                  >
                    Forgot password?
                  </Link>
                </div>
                <input
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full border border-logidex-border rounded-[10px] bg-slate-50 text-[0.88rem] text-logidex-text-dark px-[14px] py-[10px] outline-none transition-all duration-150 focus:border-logidex-blue focus:bg-white focus:ring focus:ring-logidex-blue/[.12] focus:ring-offset-0"
                />
              </div>

              <div className="h-1" />

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-logidex-blue hover:bg-logidex-blue-hover disabled:opacity-60 text-white rounded-[10px] font-semibold text-[0.9rem] h-11 tracking-[0.01em] cursor-pointer transition-colors duration-150 border-none"
              >
                {loading ? "Signing in…" : "Sign In"}
              </button>

            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
