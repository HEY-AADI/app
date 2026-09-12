import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { Bell, ChevronRight, CircleHelp, LogOut, Menu, Settings2 } from "lucide-react";
import SiteHeader from "@/components/SiteHeader";
import { navItems, roleLabels, type Role } from "@/data/mock";
import { endSession } from "@/lib/session";

type ShellMode = "demo" | "real";

export default function DashboardShell({ children, role, onRoleChange, mode = "demo" }: { children: ReactNode; role: Role; onRoleChange?: (role: Role) => void; mode?: ShellMode }) {
  const location = useLocation();
  const prefix = mode === "demo" ? "/demo" : "/app";

  return (
    <div className="min-h-screen bg-[#F8FAF6]" data-testid="dashboard-shell">
      <SiteHeader role={role} onRoleChange={onRoleChange} />
      <div className="mx-auto flex max-w-[1500px]">
        <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white/60 px-4 py-6 lg:block" data-testid="dashboard-sidebar">
          <div className="mb-7 rounded-xl bg-[#0B3C2A] p-4 text-white">
            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-amber-200">Viewing as</p>
            <p className="mt-2 font-semibold" data-testid="active-persona-name">{roleLabels[role].person}</p>
            <p className="mt-1 text-xs text-emerald-100">{roleLabels[role].label} {mode === "demo" ? "demo persona" : "secure account"}</p>
          </div>
          <nav className="space-y-1" aria-label="Workspace navigation">
            {role === "student" ? <StudentNav prefix={prefix} pathname={location.pathname} /> : <RoleNav role={role} prefix={prefix} mode={mode} />}
          </nav>
          <div className="mt-12 border-t border-slate-200 pt-4">
            <Link to="/faq" className="flex items-center gap-3 px-3 py-2 text-sm text-slate-500 hover:text-[#0B3C2A]" data-testid="sidebar-help-link"><CircleHelp size={16} />Help centre</Link>
            <button className="flex w-full items-center gap-3 px-3 py-2 text-sm text-slate-500 hover:text-[#0B3C2A]" data-testid="sidebar-settings-button"><Settings2 size={16} />Settings</button>
            {role === "student" && <button onClick={() => mode === "real" ? endSession("/login") : window.location.assign("/")} className="flex w-full items-center gap-3 px-3 py-2 text-sm text-slate-500 hover:text-[#0B3C2A]" data-testid="sidebar-logout-button"><LogOut size={16} />{mode === "real" ? "Sign out" : "Exit demo"}</button>}
          </div>
        </aside>
        <main className="min-w-0 flex-1">
          <div className="flex items-center justify-between border-b border-slate-200 bg-white/40 px-4 py-3 sm:px-8 lg:hidden">
            <button className="inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-[#0B3C2A]" data-testid="mobile-dashboard-menu"><Menu size={16} />Menu</button>
            <span className="text-xs font-semibold text-slate-500">{roleLabels[role].label} workspace</span>
            <button className="rounded-md p-2 text-slate-500" aria-label="Notifications" data-testid="mobile-notifications-button"><Bell size={17} /></button>
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}

function StudentNav({ prefix, pathname }: { prefix: string; pathname: string }) {
  const items: readonly (readonly [string, string])[] = prefix === "/app" ? [
    ["Overview", "overview"], ["Profile", "profile"], ["Skill Graph", "skills"],
    ["Pariksha", "pariksha"], ["My Experience", "karma"], ["Alumni", "alumni"],
    ["Mentors", "mentors"], ["Career Passport", "pramana"],
  ] : navItems;
  return <>{items.map(([label, slug]) => {
    const href = slug === "opportunities" ? `${prefix}/student` : `${prefix}/student/${slug}`;
    const active = pathname.includes(slug) || (slug === "overview" && pathname === `${prefix}/student`);
    return <Link key={slug} to={href} className={`flex items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${active ? "bg-emerald-50 text-[#0B3C2A]" : "text-slate-600 hover:bg-slate-50 hover:text-[#0B3C2A]"}`} data-testid={`sidebar-nav-${slug}`}><span>{label}</span>{active && <ChevronRight size={15} />}</Link>;
  })}</>;
}

function RoleNav({ role, prefix, mode }: { role: Exclude<Role, "student">; prefix: string; mode: ShellMode }) {
  const sets: Record<Exclude<Role, "student">, [string, string][]> = {
    employer: [["Dashboard", "overview"], ["Opportunities", "opportunities"], ["Applications", "applications"], ["Internships", "internships"], ["Talent", "talent"], ["Analytics", "analytics"]],
    alumni: [["My profile", "overview"], ["Mentoring", "mentors"], ["Sessions", "sessions"], ["Industry insights", "insights"]],
    institution: [["Dashboard", "overview"], ["Students", "students"], ["Internships", "internships"], ["Skill gaps", "skills"], ["Reports", "reports"]],
    ministry: [["Overview", "overview"], ["Demand", "demand"], ["Skills", "skills"], ["Districts", "districts"], ["Fairness", "fairness"]],
  };
  return <>{sets[role].map(([label, slug]) => <Link key={slug} to={`${prefix}/${role}/${slug}`} className="flex items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 hover:text-[#0B3C2A]" data-testid={`sidebar-nav-${slug}`}><span>{label}</span><ChevronRight size={15} /></Link>)}<button onClick={() => mode === "real" ? endSession("/login") : window.location.assign("/")} className="mt-4 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-500 hover:bg-slate-50" data-testid="sidebar-logout-button"><LogOut size={16} />{mode === "real" ? "Sign out" : "Exit demo"}</button></>;
}