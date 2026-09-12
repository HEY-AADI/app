import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, CheckCircle2, Eye, EyeOff, ShieldCheck } from "lucide-react";
import BrandMark from "@/components/BrandMark";
import { apiPost, ApiError } from "@/lib/api";
import { beginSession } from "@/lib/session";
import type { Role, SessionResponse } from "@/lib/types";

const credentials: Array<{ role: Role; label: string; email: string }> = [
  { role: "student", label: "Student · Ananya Sharma", email: "student@demo.samanvaya.in" },
  { role: "employer", label: "Employer · Dabur Research Labs", email: "employer@demo.samanvaya.in" },
  { role: "alumni", label: "Alumni / Mentor · Dr. Rajesh Vaidya", email: "alumni@demo.samanvaya.in" },
  { role: "institution", label: "Institution · National Institute of Ayurveda", email: "institution@demo.samanvaya.in" },
  { role: "ministry", label: "Ministry · Policy workspace", email: "ministry@demo.samanvaya.in" },
];

export default function Login() {
  const [email, setEmail] = useState("student@demo.samanvaya.in");
  const [password, setPassword] = useState("AyushDemo@2026");
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const next = new URLSearchParams(location.search).get("next");
  const login = useMutation({
    mutationFn: () => apiPost<SessionResponse>("/auth/login", { email, password }),
    onSuccess: ({ user }) => { beginSession(); navigate(next ?? `/app/${user.role}`, { replace: true }); },
  });
  const error = login.error instanceof ApiError && typeof login.error.body === "object" && login.error.body && "detail" in login.error.body ? String(login.error.body.detail) : login.error ? "We could not sign you in. Check the demo credentials and try again." : "";
  return <div className="min-h-screen bg-[#F8FAF6]" data-testid="login-page"><header className="border-b border-slate-200 bg-white"><div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8"><Link to="/" data-testid="login-home-link"><BrandMark /></Link><Link to="/demo/student" className="text-sm font-semibold text-[#0B3C2A]" data-testid="login-demo-link">Explore Demo mode →</Link></div></header><main className="mx-auto grid max-w-6xl gap-12 px-4 py-12 sm:px-6 lg:grid-cols-[.8fr_1.2fr] lg:items-center lg:px-8 lg:py-20"><div><p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] text-amber-700">SECURE ROLE ACCESS</p><h1 className="mt-4 text-4xl font-bold tracking-tight text-[#0B3C2A] sm:text-5xl">Sign in to your SAMANVAYA workspace.</h1><p className="mt-5 max-w-lg text-base leading-7 text-slate-600">Use a seeded role account to explore the persistent Phase 2 flows. Sessions are httpOnly and role-protected.</p><div className="mt-8 flex items-center gap-3 text-sm text-emerald-800"><ShieldCheck size={18} /><span>Demo accounts · secure session prototype</span></div></div><div className="rounded-xl border border-slate-200 bg-white p-6 shadow-[0_18px_50px_rgba(11,60,42,.08)] sm:p-8"><form onSubmit={(event) => { event.preventDefault(); login.mutate(); }} data-testid="login-form"><h2 className="text-xl font-bold text-[#0B3C2A]">Sign in</h2><label className="mt-6 block text-sm font-semibold text-slate-700">Email<input value={email} onChange={(event) => setEmail(event.target.value)} type="email" className="mt-2 h-11 w-full rounded-md border border-slate-200 px-3 text-sm outline-none focus:border-[#0B3C2A] focus:ring-2 focus:ring-emerald-100" data-testid="login-email-input" /></label><label className="mt-4 block text-sm font-semibold text-slate-700">Password<div className="relative mt-2"><input value={password} onChange={(event) => setPassword(event.target.value)} type={showPassword ? "text" : "password"} className="h-11 w-full rounded-md border border-slate-200 px-3 pr-11 text-sm outline-none focus:border-[#0B3C2A] focus:ring-2 focus:ring-emerald-100" data-testid="login-password-input" /><button type="button" onClick={() => setShowPassword((visible) => !visible)} className="absolute right-2 top-2 rounded p-1.5 text-slate-400" aria-label={showPassword ? "Hide password" : "Show password"} data-testid="login-password-toggle">{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div></label>{error && <p className="mt-4 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-800" role="alert" data-testid="login-error-message">{error}</p>}<button disabled={login.isPending} className="mt-6 flex h-11 w-full items-center justify-center gap-2 rounded-md bg-[#0B3C2A] text-sm font-bold text-white disabled:opacity-60" data-testid="login-submit-button">{login.isPending ? "Signing in…" : "Sign in securely"}<ArrowRight size={16} /></button></form><div className="mt-8 border-t border-slate-100 pt-6"><div className="flex items-center justify-between"><p className="text-xs font-bold uppercase tracking-[0.14em] text-amber-700">DEMO CREDENTIALS</p><span className="text-[11px] text-slate-400">Password for all: AyushDemo@2026</span></div><div className="mt-3 space-y-2">{credentials.map((item) => <button key={item.role} type="button" onClick={() => { setEmail(item.email); setPassword("AyushDemo@2026"); }} className="flex w-full items-center justify-between rounded-md border border-slate-100 px-3 py-2 text-left text-xs hover:border-amber-300 hover:bg-amber-50" data-testid={`demo-credential-${item.role}`}><span className="font-semibold text-[#0B3C2A]">{item.label}</span><CheckCircle2 size={14} className="text-emerald-600" /></button>)}</div></div></div></main></div>;
}