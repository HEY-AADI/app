import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, Eye, EyeOff, ShieldCheck } from "lucide-react";
import BrandMark from "@/components/BrandMark";
import { apiPost, ApiError } from "@/lib/api";
import { beginSession } from "@/lib/session";
import type { SessionResponse } from "@/lib/types";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const next = new URLSearchParams(location.search).get("next");
  const login = useMutation({
    mutationFn: () => apiPost<SessionResponse>("/auth/login", { email, password }),
    onSuccess: ({ user }) => {
      beginSession();
      navigate(next ?? `/app/${user.role}`, { replace: true });
    },
  });
  const error = login.error instanceof ApiError && typeof login.error.body === "object" && login.error.body && "detail" in login.error.body
    ? String(login.error.body.detail)
    : login.error ? "We could not sign you in. Check your details and try again." : "";

  return (
    <div className="min-h-screen bg-slate-50" data-testid="login-page">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex min-h-20 max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
          <Link to="/" data-testid="login-home-link"><BrandMark testIdPrefix="login-header" /></Link>
          <Link to="/demo/student" className="text-sm font-semibold text-[#174A3A]" data-testid="login-demo-link">Explore Demo mode →</Link>
        </div>
      </header>
      <main className="mx-auto grid max-w-6xl gap-12 px-4 py-12 sm:px-6 lg:grid-cols-[.9fr_1.1fr] lg:items-center lg:px-8 lg:py-20">
        <div>
          <p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-[#A66D12]" data-testid="login-eyebrow">SECURE ROLE ACCESS</p>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl" data-testid="login-title">Sign in to your SAMANVAYA workspace.</h1>
          <p className="mt-5 max-w-lg text-base leading-7 text-slate-600" data-testid="login-description">Protected sessions connect your profile, applications, assessment history and internship evidence.</p>
          <div className="mt-8 flex items-center gap-3 text-sm text-[#174A3A]"><ShieldCheck size={18} /><span>Role-protected access · httpOnly session</span></div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,.07)] sm:p-8">
          <form onSubmit={(event) => { event.preventDefault(); login.mutate(); }} data-testid="login-form">
            <h2 className="text-xl font-bold text-slate-900">Sign in</h2>
            <label className="mt-6 block text-sm font-semibold text-slate-700">Email
              <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" autoComplete="email" required className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-[#174A3A] focus:ring-2 focus:ring-emerald-100" data-testid="login-email-input" />
            </label>
            <label className="mt-4 block text-sm font-semibold text-slate-700">Password
              <div className="relative mt-2"><input value={password} onChange={(event) => setPassword(event.target.value)} type={showPassword ? "text" : "password"} autoComplete="current-password" required className="h-11 w-full rounded-md border border-slate-300 px-3 pr-11 text-sm outline-none focus:border-[#174A3A] focus:ring-2 focus:ring-emerald-100" data-testid="login-password-input" /><button type="button" onClick={() => setShowPassword((visible) => !visible)} className="absolute right-2 top-2 rounded p-1.5 text-slate-500" aria-label={showPassword ? "Hide password" : "Show password"} data-testid="login-password-toggle">{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>
            </label>
            {error && <p className="mt-4 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-800" role="alert" data-testid="login-error-message">{error}</p>}
            <button disabled={login.isPending} className="mt-6 flex h-11 w-full items-center justify-center gap-2 rounded-md bg-[#174A3A] text-sm font-bold text-white disabled:opacity-60" data-testid="login-submit-button">{login.isPending ? "Signing in…" : "Sign in securely"}<ArrowRight size={16} /></button>
          </form>
          <p className="mt-6 border-t border-slate-100 pt-5 text-xs leading-5 text-slate-500" data-testid="login-credential-help">Access details are provided to authorised evaluators and documented in the project README. Credentials are not displayed in the application.</p>
        </div>
      </main>
    </div>
  );
}