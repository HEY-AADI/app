import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Plus, Save, Trash2 } from "lucide-react";
import DashboardShell from "@/components/DashboardShell";
import { apiGet, apiPatch } from "@/lib/api";
import type { PortfolioEvidence, SkillEntry, SkillProvenance, StudentProfile, StudentProfileUpdate } from "@/lib/types";

const provenanceOptions: SkillProvenance[] = ["Self-declared", "Institution verified", "Employer verified", "Issuer verified"];

export default function StudentProfilePage() {
  const profile = useQuery({ queryKey: ["profile", "me"], queryFn: () => apiGet<StudentProfile>("/profile/me") });
  return (
    <DashboardShell role="student" mode="real">
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-8" data-testid="student-profile-page">
        <p className="font-mono text-xs font-semibold uppercase tracking-[0.17em] text-[#A66D12]">PRAMANA · PROFILE & EVIDENCE</p>
        <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Build a profile that shows where your skills came from.</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">Save education, career interests, skill confidence and evidence provenance to your PostgreSQL-backed profile.</p>
        {profile.isPending && <div className="mt-8 rounded-xl border border-slate-200 bg-white p-8 text-sm text-slate-500" data-testid="profile-loading-state">Loading your saved profile…</div>}
        {profile.isError && <div className="mt-8 rounded-xl border border-rose-200 bg-rose-50 p-6 text-sm text-rose-800" data-testid="profile-error-state">We couldn’t load your profile. Your saved data is safe; please try again.</div>}
        {profile.data && <ProfileEditor profile={profile.data} />}
      </div>
    </DashboardShell>
  );
}

function ProfileEditor({ profile }: { profile: StudentProfile }) {
  const queryClient = useQueryClient();
  const [education, setEducation] = useState(profile.education);
  const [ayushSystem, setAyushSystem] = useState<StudentProfile["ayush_system"]>(profile.ayush_system);
  const [graduationYear, setGraduationYear] = useState(profile.graduation_year);
  const [interests, setInterests] = useState(profile.interests.join(", "));
  const [skills, setSkills] = useState<SkillEntry[]>(profile.skills);
  const [evidence, setEvidence] = useState<PortfolioEvidence[]>(profile.portfolio_evidence);
  const save = useMutation({
    mutationFn: (payload: StudentProfileUpdate) => apiPatch<StudentProfile>("/profile/me", payload),
    onSuccess: (updated) => queryClient.setQueryData(["profile", "me"], updated),
  });
  const updateSkill = (index: number, patch: Partial<SkillEntry>) => setSkills((current) => current.map((skill, position) => position === index ? { ...skill, ...patch } : skill));
  const updateEvidence = (index: number, patch: Partial<PortfolioEvidence>) => setEvidence((current) => current.map((item, position) => position === index ? { ...item, ...patch } : item));
  const submit = () => save.mutate({ education, ayush_system: ayushSystem, graduation_year: graduationYear, interests: interests.split(",").map((item) => item.trim()).filter(Boolean), skills, portfolio_evidence: evidence });

  return <div className="mt-8 space-y-6">
    <section className="rounded-xl border border-slate-200 bg-white p-6 sm:p-8" data-testid="profile-identity-section">
      <div className="flex items-start justify-between gap-4"><div><h2 className="text-xl font-bold text-slate-900">Education and direction</h2><p className="mt-1 text-sm text-slate-500">Signed in as {profile.name} · {profile.institution}</p></div><span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-[#174A3A]">Private profile</span></div>
      <div className="mt-6 grid gap-5 sm:grid-cols-2">
        <label className="text-sm font-semibold text-slate-700">Education<input value={education} onChange={(event) => setEducation(event.target.value)} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 font-normal" data-testid="profile-education-input" /></label>
        <label className="text-sm font-semibold text-slate-700">AYUSH system<select value={ayushSystem} onChange={(event) => setAyushSystem(event.target.value as StudentProfile["ayush_system"])} className="mt-2 h-11 w-full rounded-md border border-slate-300 bg-white px-3 font-normal" data-testid="profile-system-select">{["Ayurveda", "Siddha", "Unani", "Homoeopathy", "Yoga & Naturopathy"].map((item) => <option key={item}>{item}</option>)}</select></label>
        <label className="text-sm font-semibold text-slate-700">Graduation year<input type="number" min={2020} max={2040} value={graduationYear} onChange={(event) => setGraduationYear(Number(event.target.value))} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 font-normal" data-testid="profile-graduation-year-input" /></label>
        <label className="text-sm font-semibold text-slate-700">Career interests<input value={interests} onChange={(event) => setInterests(event.target.value)} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 font-normal" data-testid="profile-interests-input" /><span className="mt-1 block text-xs font-normal text-slate-500">Separate interests with commas.</span></label>
      </div>
    </section>

    <section className="rounded-xl border border-slate-200 bg-white p-6 sm:p-8" data-testid="profile-skills-section">
      <div className="flex items-center justify-between gap-4"><div><h2 className="text-xl font-bold text-slate-900">Skills and provenance</h2><p className="mt-1 text-sm text-slate-500">Verified evidence should carry more confidence than self-declaration.</p></div><button onClick={() => setSkills((current) => [...current, { name: "New skill", level: 50, provenance: "Self-declared", evidence: "" }])} className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-[#174A3A]" data-testid="profile-add-skill-button"><Plus size={15} />Add skill</button></div>
      <div className="mt-6 space-y-4">{skills.map((skill, index) => <div key={`${skill.name}-${index}`} className="grid gap-3 rounded-lg border border-slate-200 p-4 md:grid-cols-[1fr_120px_190px_1.2fr_auto]" data-testid={`profile-skill-row-${index}`}><input value={skill.name} onChange={(event) => updateSkill(index, { name: event.target.value })} aria-label={`Skill ${index + 1} name`} className="h-10 rounded-md border border-slate-300 px-3 text-sm" data-testid={`profile-skill-name-${index}`} /><input type="number" min={0} max={100} value={skill.level} onChange={(event) => updateSkill(index, { level: Number(event.target.value) })} aria-label={`Skill ${index + 1} level`} className="h-10 rounded-md border border-slate-300 px-3 text-sm" data-testid={`profile-skill-level-${index}`} /><select value={skill.provenance} onChange={(event) => updateSkill(index, { provenance: event.target.value as SkillProvenance })} aria-label={`Skill ${index + 1} provenance`} className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm" data-testid={`profile-skill-provenance-${index}`}>{provenanceOptions.map((item) => <option key={item}>{item}</option>)}</select><input value={skill.evidence} onChange={(event) => updateSkill(index, { evidence: event.target.value })} aria-label={`Skill ${index + 1} evidence`} placeholder="Evidence or source" className="h-10 rounded-md border border-slate-300 px-3 text-sm" data-testid={`profile-skill-evidence-${index}`} /><button onClick={() => setSkills((current) => current.filter((_, position) => position !== index))} aria-label={`Remove ${skill.name}`} className="rounded-md p-2 text-slate-500 hover:bg-rose-50 hover:text-rose-700" data-testid={`profile-remove-skill-${index}`}><Trash2 size={16} /></button></div>)}</div>
    </section>

    <section className="rounded-xl border border-slate-200 bg-white p-6 sm:p-8" data-testid="profile-evidence-section">
      <div className="flex items-center justify-between gap-4"><div><h2 className="text-xl font-bold text-slate-900">Portfolio evidence</h2><p className="mt-1 text-sm text-slate-500">Add traceable work, assessments, internships or certifications.</p></div><button onClick={() => setEvidence((current) => [...current, { title: "New evidence", issuer: profile.institution ?? "To be verified", evidence_type: "Project", date: new Date().toISOString().slice(0, 10) }])} className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-[#174A3A]" data-testid="profile-add-evidence-button"><Plus size={15} />Add evidence</button></div>
      <div className="mt-6 space-y-4">{evidence.map((item, index) => <div key={`${item.title}-${index}`} className="grid gap-3 rounded-lg border border-slate-200 p-4 md:grid-cols-[1.2fr_1fr_160px_150px]" data-testid={`profile-evidence-row-${index}`}><input value={item.title} onChange={(event) => updateEvidence(index, { title: event.target.value })} aria-label={`Evidence ${index + 1} title`} className="h-10 rounded-md border border-slate-300 px-3 text-sm" data-testid={`profile-evidence-title-${index}`} /><input value={item.issuer} onChange={(event) => updateEvidence(index, { issuer: event.target.value })} aria-label={`Evidence ${index + 1} issuer`} className="h-10 rounded-md border border-slate-300 px-3 text-sm" data-testid={`profile-evidence-issuer-${index}`} /><select value={item.evidence_type} onChange={(event) => updateEvidence(index, { evidence_type: event.target.value as PortfolioEvidence["evidence_type"] })} aria-label={`Evidence ${index + 1} type`} className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm" data-testid={`profile-evidence-type-${index}`}>{["Project", "Internship", "Certification", "Assessment"].map((type) => <option key={type}>{type}</option>)}</select><input type="date" value={item.date} onChange={(event) => updateEvidence(index, { date: event.target.value })} aria-label={`Evidence ${index + 1} date`} className="h-10 rounded-md border border-slate-300 px-3 text-sm" data-testid={`profile-evidence-date-${index}`} /></div>)}</div>
    </section>

    <div className="flex items-center justify-end gap-4"><span className="text-sm text-[#174A3A]" data-testid="profile-save-status">{save.isSuccess ? <><CheckCircle2 size={16} className="mr-1 inline" />Profile saved</> : save.isError ? "We couldn’t save your profile. Please try again." : ""}</span><button onClick={submit} disabled={save.isPending} className="inline-flex items-center gap-2 rounded-md bg-[#174A3A] px-5 py-3 text-sm font-bold text-white disabled:opacity-60" data-testid="profile-save-button"><Save size={16} />{save.isPending ? "Saving…" : "Save profile"}</button></div>
  </div>;
}