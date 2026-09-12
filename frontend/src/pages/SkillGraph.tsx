import { useQuery } from "@tanstack/react-query";
import { ArrowRight, BadgeCheck, BookOpenCheck, ExternalLink, GitBranch } from "lucide-react";
import DashboardShell from "@/components/DashboardShell";
import { apiGet } from "@/lib/api";
import type { AssessmentResult, StudentProfile } from "@/lib/types";

const certifications = [
  { skill: "Panchakarma", title: "Panchakarma Assistant — HSS/Q3603", provider: "Healthcare Sector Skill Council · NSQF", level: "NSQF Level 3", url: "https://www.healthcare-ssc.in/pdf/New25/MC_Panchakarma_Assistant.pdf" },
  { skill: "Panchakarma", title: "Panchakarma Technician Certificate Course", provider: "National Institute of Ayurveda", level: "Institution certificate", url: "https://nia.nic.in/pdf/Panchkarma_Technician_Certificate_Course_11feb25.pdf" },
  { skill: "Clinical operations", title: "Panchakarma Assistant — Course 666", provider: "National Institute of Open Schooling", level: "Vocational course", url: "https://rcallahabad.nios.ac.in/panchakarma-assistant-666.html" },
];

export default function SkillGraph() {
  const profile = useQuery({ queryKey: ["profile", "me"], queryFn: () => apiGet<StudentProfile>("/profile/me") });
  const latest = useQuery({ queryKey: ["assessment", "latest"], queryFn: () => apiGet<AssessmentResult | null>("/assessments/latest") });
  const gap = latest.data?.gaps[0] ?? "GMP fundamentals";
  return <DashboardShell role="student" mode="real"><div className="mx-auto max-w-6xl px-4 py-10 sm:px-8" data-testid="skill-graph-page">
    <p className="font-mono text-xs font-semibold uppercase tracking-[0.17em] text-[#A66D12]">LAYER 0 · AYUSH SKILL GRAPH</p>
    <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">See how one skill opens the next role.</h1>
    <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">Your profile and Pariksha evidence shape this pathway. Certification suggestions link to authoritative providers; SAMANVAYA does not enrol or verify them.</p>
    <section className="mt-8 rounded-xl border border-slate-200 bg-white p-6 sm:p-8" data-testid="skill-graph-visual">
      <div className="flex items-center gap-2 text-sm font-semibold text-[#174A3A]"><GitBranch size={18} />Recommended pathway for {profile.data?.name ?? "your profile"}</div>
      <div className="mt-7 grid gap-3 md:grid-cols-5">{["BAMS foundation", gap, "Quality documentation", "QA internship", "Quality associate"].map((node, index) => <div key={node} className="relative rounded-lg border border-slate-200 bg-slate-50 p-4" data-testid={`skill-graph-node-${index}`}><span className="font-mono text-[10px] text-[#A66D12]">0{index + 1}</span><p className="mt-2 text-sm font-bold text-slate-900">{node}</p>{index < 4 && <ArrowRight className="absolute -right-5 top-1/2 z-10 hidden -translate-y-1/2 text-[#A66D12] md:block" size={20} />}</div>)}</div>
      <div className="mt-6 rounded-lg border-l-4 border-[#C58B2A] bg-amber-50 p-4 text-sm text-amber-950" data-testid="skill-graph-gap-note"><strong>Why this path:</strong> {gap} is a current assessment gap and appears in the quality-associate opportunity pathway.</div>
    </section>
    <section className="mt-10" data-testid="certification-recommendations"><div className="flex items-end justify-between gap-4"><div><p className="font-mono text-xs font-semibold uppercase tracking-[0.15em] text-[#A66D12]">CREDIBLE NEXT STEPS</p><h2 className="mt-2 text-2xl font-bold text-slate-900">Certification and training sources</h2></div><BadgeCheck className="text-[#174A3A]" /></div>
      <div className="mt-5 grid gap-5 lg:grid-cols-3">{certifications.map((item, index) => <article key={item.title} className="rounded-xl border border-slate-200 bg-white p-6" data-testid={`certification-card-${index}`}><BookOpenCheck size={20} className="text-[#A66D12]" /><p className="mt-5 text-xs font-semibold uppercase tracking-wider text-[#A66D12]">{item.skill}</p><h3 className="mt-2 text-lg font-bold text-slate-900">{item.title}</h3><p className="mt-2 text-sm text-slate-600">{item.provider}</p><p className="mt-1 text-xs text-slate-500">{item.level}</p><a href={item.url} target="_blank" rel="noreferrer" className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-[#174A3A]" data-testid={`certification-source-link-${index}`}>Open official source <ExternalLink size={14} /></a><p className="mt-3 text-[11px] leading-5 text-slate-500">Verify current eligibility, intake, fees and recognition directly with the provider before applying.</p></article>)}</div>
    </section>
  </div></DashboardShell>;
}