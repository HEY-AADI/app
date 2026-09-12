import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ArrowRight, CheckCircle2, ClipboardCheck, LogOut, ShieldCheck, Sparkles } from "lucide-react";
import SiteHeader from "@/components/SiteHeader";
import { apiGet, apiPost } from "@/lib/api";
import { endSession } from "@/lib/session";
import { useAuth } from "@/hooks/useAuth";
import type { PersistedApplication, PersistedInternship, PersistedOpportunity } from "@/lib/types";

export default function AuthenticatedWorkspace() {
  const auth = useAuth();
  const queryClient = useQueryClient();
  const opportunities = useQuery({ queryKey: ["opportunities"], queryFn: () => apiGet<PersistedOpportunity[]>("/opportunities") });
  const applications = useQuery({ queryKey: ["applications", "me"], queryFn: () => apiGet<PersistedApplication[]>("/applications/me") });
  const internships = useQuery({ queryKey: ["internships", "me"], queryFn: () => apiGet<PersistedInternship[]>("/internships/me") });
  const apply = useMutation({
    mutationFn: (id: string) => apiPost<PersistedApplication>(`/opportunities/${id}/apply`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications", "me"] });
      queryClient.invalidateQueries({ queryKey: ["internships", "me"] });
    },
  });
  const internship = internships.data?.[0];

  return (
    <div className="min-h-screen bg-[#F8FAF6]" data-testid="authenticated-student-workspace">
      <SiteHeader role="student" />
      <div className="border-b border-amber-200 bg-amber-50/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-2 text-xs text-amber-900 sm:px-6 lg:px-8">
          <span data-testid="workspace-session-summary"><strong>Secure workspace:</strong> {auth.data?.name} · {auth.data?.role}</span>
          <button onClick={() => endSession("/login")} className="inline-flex items-center gap-1 font-semibold" data-testid="workspace-logout-button"><LogOut size={13} />Sign out</button>
        </div>
      </div>
      <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.17em] text-amber-700" data-testid="workspace-eyebrow">PERSISTENT STUDENT WORKSPACE</p>
            <h1 className="mt-3 text-3xl font-bold tracking-tight text-[#0B3C2A] sm:text-4xl" data-testid="workspace-greeting">Good morning, {auth.data?.name.split(" ")[0]}.</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600" data-testid="workspace-description">Your secure session connects your profile, saved applications, internships and assessment history.</p>
          </div>
          <Link to="/app/student/pariksha" className="inline-flex items-center gap-2 rounded-md bg-[#0B3C2A] px-4 py-2.5 text-sm font-bold text-white" data-testid="workspace-assessment-link"><Sparkles size={16} />Take Pariksha</Link>
        </div>

        <div className="mt-8 grid gap-5 lg:grid-cols-[1.15fr_.85fr]">
          <section className="rounded-xl bg-[#0B3C2A] p-6 text-white sm:p-8" data-testid="persistent-readiness-card">
            <p className="font-mono text-xs uppercase tracking-[0.16em] text-amber-200">YOUR SAVED READINESS</p>
            <div className="mt-3 flex items-end gap-2"><span className="font-mono text-6xl font-semibold" data-testid="persistent-readiness-score">{auth.data?.readiness ?? 0}%</span><span className="mb-2 text-sm text-emerald-100/70">profile signal</span></div>
            <p className="mt-3 text-sm leading-6 text-emerald-100/75">Complete Pariksha to update this score and get sharper match explanations.</p>
            <div className="mt-6 h-2 rounded-full bg-white/10"><div className="h-full rounded-full bg-amber-400" style={{ width: `${auth.data?.readiness ?? 0}%` }} /></div>
          </section>
          <section className="rounded-xl border border-amber-200 bg-amber-50 p-6" data-testid="persistent-application-summary">
            <p className="font-mono text-xs font-bold uppercase tracking-[0.14em] text-amber-800">MY EXPERIENCE</p>
            <p className="mt-4 text-3xl font-bold text-[#0B3C2A]" data-testid="persistent-application-count">{applications.data?.length ?? 0} applications</p>
            <p className="mt-2 text-sm leading-6 text-amber-950/70">Every application is stored against your signed-in profile. {internship ? "Your internship tracker is ready." : "Apply to start your internship record."}</p>
            <Link to="#applications" className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-amber-900" data-testid="persistent-applications-link">View applications <ArrowRight size={15} /></Link>
          </section>
        </div>

        <section className="mt-10" data-testid="persistent-opportunities-section">
          <div className="flex items-end justify-between gap-4">
            <div><p className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-amber-700">YOJANA · PERSISTED OPPORTUNITIES</p><h2 className="mt-2 text-xl font-bold text-[#0B3C2A]">Recommended next steps</h2></div>
            <span className="text-xs text-slate-500" data-testid="workspace-persistence-label">Loaded from PostgreSQL</span>
          </div>
          <div className="mt-4 grid gap-5 lg:grid-cols-3">
            {opportunities.data?.map((opportunity) => (
              <article key={opportunity.id} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm" data-testid={`persistent-opportunity-${opportunity.id}`}>
                <div className="flex items-start justify-between gap-3"><div><span className="rounded-sm bg-amber-50 px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-amber-800">{opportunity.type}</span><h3 className="mt-3 font-bold text-[#0B3C2A]">{opportunity.title}</h3><p className="mt-1 text-xs text-slate-500">{opportunity.organisation} · {opportunity.location}</p></div><span className="font-mono text-lg font-semibold text-[#0B3C2A]">{opportunity.match}%</span></div>
                <div className="mt-5 flex items-center gap-2 text-xs text-slate-600"><ShieldCheck size={14} className="text-emerald-600" />{opportunity.mentor} · mentor assigned</div>
                <button disabled={apply.isPending || applications.data?.some((item) => item.opportunity_id === opportunity.id)} onClick={() => apply.mutate(opportunity.id)} className="mt-5 flex w-full items-center justify-center gap-2 rounded-md bg-[#D97706] py-2.5 text-xs font-bold text-white disabled:cursor-not-allowed disabled:bg-slate-300" data-testid={`persistent-apply-${opportunity.id}`}>{applications.data?.some((item) => item.opportunity_id === opportunity.id) ? "Application saved" : "Apply and save"}<ArrowRight size={14} /></button>
              </article>
            ))}
          </div>
          {opportunities.isPending && <p className="mt-6 text-sm text-slate-500" data-testid="persistent-opportunities-loading">Loading persisted opportunities…</p>}
          {opportunities.isError && <p className="mt-6 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800" data-testid="persistent-opportunities-error">We couldn’t load your opportunities. Your application data is safe; please try again.</p>}
        </section>

        <section id="applications" className="mt-10 grid gap-6 lg:grid-cols-2" data-testid="persistent-progress-section">
          <div className="rounded-xl border border-slate-200 bg-white p-6">
            <div className="flex items-center gap-2"><ClipboardCheck size={18} className="text-amber-700" /><h2 className="font-bold text-[#0B3C2A]">Application history</h2></div>
            <div className="mt-5 space-y-3">
              {applications.data?.length ? applications.data.map((application) => <div key={application.id} className="rounded-lg bg-slate-50 p-4" data-testid={`application-record-${application.id}`}><div className="flex justify-between gap-3"><div><p className="text-sm font-bold text-[#0B3C2A]">{application.opportunity_title}</p><p className="mt-1 text-xs text-slate-500">{application.organisation}</p></div><span className="rounded-full bg-amber-50 px-2 py-1 text-[10px] font-semibold text-amber-800">{application.status}</span></div><p className="mt-3 text-xs leading-5 text-slate-600">Next: {application.next_action}</p></div>) : <p className="text-sm text-slate-500" data-testid="applications-empty-state">No applications yet. Save your first opportunity above.</p>}
            </div>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-6">
            <div className="flex items-center gap-2"><CheckCircle2 size={18} className="text-emerald-700" /><h2 className="font-bold text-[#0B3C2A]">Internship milestones</h2></div>
            {internship ? <div className="mt-5"><p className="text-sm font-bold text-[#0B3C2A]">{internship.opportunity_title}</p><p className="mt-1 text-xs text-slate-500">{internship.week} of {internship.total_weeks} weeks · {internship.mentor}</p><div className="mt-5 space-y-3">{internship.milestones.map((milestone) => <div key={milestone.id} className="flex items-start gap-3" data-testid={`milestone-${milestone.id}`}><span className={`mt-1 h-2.5 w-2.5 rounded-full ${milestone.status === "active" ? "bg-amber-500" : "bg-slate-300"}`} /><div><p className="text-sm font-semibold text-slate-700">{milestone.title}</p><p className="mt-1 text-xs text-slate-500">{milestone.detail}</p></div></div>)}</div><div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900"><strong>Next:</strong> mentor assignment is unlocked after employer review.</div></div> : <p className="mt-5 text-sm text-slate-500" data-testid="internship-empty-state">Your saved application will create a milestone tracker here.</p>}
          </div>
        </section>
      </main>
    </div>
  );
}