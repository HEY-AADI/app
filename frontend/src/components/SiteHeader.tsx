import { Link, useLocation } from "react-router-dom";
import { Menu, Search, ChevronDown } from "lucide-react";
import BrandMark from "@/components/BrandMark";
import { roleLabels, type Role } from "@/data/mock";

export default function SiteHeader({ role = "student", onRoleChange }: { role?: Role; onRoleChange?: (role: Role) => void }) {
  const location = useLocation();
  const isWorkspace = location.pathname.startsWith("/app");
  return (
    <>
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-[#F8FAF6]/95 backdrop-blur-md" data-testid="site-header">
        <div className="mx-auto flex h-[76px] max-w-7xl items-center justify-between gap-5 px-4 sm:px-6 lg:px-8">
          <Link to="/" aria-label="SAMANVAYA home" data-testid="header-home-link"><BrandMark /></Link>
          <nav className="hidden items-center gap-6 lg:flex" aria-label="Primary navigation" data-testid="primary-navigation">
            {[["Explore", "/how-it-works"], ["Opportunities", "/opportunities"], ["Internships", "/opportunities?type=internship"], ["Alumni", "/alumni"], ["Mentors", "/mentors"]].map(([label, href]) => (
              <Link key={href} to={href} className="text-sm font-medium text-slate-600 transition-colors hover:text-[#0B3C2A]" data-testid={`header-nav-${label.toLowerCase()}`}>{label}</Link>
            ))}
          </nav>
          <div className="flex items-center gap-2 sm:gap-3">
            <button className="hidden rounded-full p-2 text-slate-500 hover:bg-slate-100 sm:inline-flex" aria-label="Search" data-testid="header-search-button"><Search size={18} /></button>
            {isWorkspace ? (
              <div className="relative hidden sm:block">
                <select value={role} onChange={(event) => onRoleChange?.(event.target.value as Role)} className="h-10 appearance-none rounded-lg border border-slate-200 bg-white py-2 pl-3 pr-9 text-xs font-semibold text-[#0B3C2A] outline-none focus:ring-2 focus:ring-amber-500" aria-label="Switch demo persona" data-testid="demo-persona-select">
                  <option value="student">Student · Ananya Sharma</option>
                  <option value="employer">AYUSH Employer · Dabur Research Labs</option>
                  <option value="alumni">Alumni / Mentor · Dr. Rajesh Vaidya</option>
                  <option value="institution">Institution · National Institute of Ayurveda</option>
                  <option value="ministry">Ministry Officer · Ministry Admin</option>
                </select>
                <ChevronDown className="pointer-events-none absolute right-2.5 top-3 text-slate-400" size={15} />
              </div>
            ) : <Link to="/app/student" className="hidden text-sm font-semibold text-[#0B3C2A] sm:inline-flex" data-testid="header-login-link">Demo sign in</Link>}
            <Link to="/app/student" className="inline-flex h-10 items-center rounded-md bg-[#0B3C2A] px-3.5 text-sm font-semibold text-white shadow-sm transition-transform hover:-translate-y-0.5 hover:bg-[#072B1E]" data-testid="header-get-started-button">Get started</Link>
            <button className="rounded-md border border-slate-200 p-2 text-[#0B3C2A] lg:hidden" aria-label="Open navigation" data-testid="mobile-menu-button"><Menu size={19} /></button>
          </div>
        </div>
      </header>
      {isWorkspace && <div className="border-b border-amber-200 bg-amber-50/80" data-testid="demo-mode-banner"><div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-2 text-xs text-amber-900 sm:px-6 lg:px-8"><span><strong>Demo mode:</strong> sample personas and simulated verification are used in this Phase 1 prototype.</span><Link to="/about" className="hidden font-semibold underline underline-offset-2 sm:inline" data-testid="demo-mode-learn-more">Learn about the prototype</Link></div></div>}
    </>
  );
}