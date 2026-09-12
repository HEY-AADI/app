import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ArrowRight, CheckCircle2, ChevronLeft, ShieldCheck, Sparkles } from "lucide-react";
import DashboardShell from "@/components/DashboardShell";
import { apiGet, apiPost } from "@/lib/api";
import type { AssessmentResult, AssessmentStart, QuestionType } from "@/lib/types";

const typeLabels: Record<QuestionType, string> = {
  mcq: "Multiple choice",
  assertion_reasoning: "Assertion–reasoning",
  case_based: "Case-based",
  scenario_based: "Scenario-based",
};

export default function Assessment() {
  const assessment = useQuery({ queryKey: ["assessment", "start"], queryFn: () => apiGet<AssessmentStart>("/assessments/start") });
  const questionList = assessment.data?.questions;
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const submit = useMutation({ mutationFn: () => apiPost<AssessmentResult>("/assessments/submit", { answers: Object.entries(answers).map(([question_id, option_index]) => ({ question_id, option_index })) }) });
  const question = questionList?.[index];
  const progress = questionList ? Math.round(((index + 1) / questionList.length) * 100) : 0;
  const answered = useMemo(() => Object.keys(answers).length, [answers]);
  if (submit.data) return <AssessmentResultView result={submit.data} />;

  return <DashboardShell role="student" mode="real"><div className="mx-auto max-w-5xl px-4 py-10 sm:px-8" data-testid="assessment-engine-page">
    <Link to="/app/student" className="inline-flex items-center gap-2 text-sm font-semibold text-[#174A3A]" data-testid="assessment-back-link"><ChevronLeft size={16} />Student workspace</Link>
    <div className="mt-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-start"><div><p className="font-mono text-xs font-semibold uppercase tracking-[0.17em] text-[#A66D12]">PARIKSHA · DETAILED ASSESSMENT</p><h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Go beyond confidence. Show how you reason.</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">25 questions: 20 core MCQs and 5 higher-order assertion–reasoning, case and scenario questions.</p></div><span className="inline-flex w-fit items-center rounded-full border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-[#174A3A]"><ShieldCheck size={14} className="mr-1" />Evidence-led</span></div>
    <div className="mt-8 flex items-center justify-between text-xs font-semibold text-slate-500"><span data-testid="assessment-progress-label">{answered} answered · {questionList?.length ?? 25} total</span><span>{progress}% through this attempt</span></div>
    <div className="mt-3 h-2 rounded-full bg-slate-100"><div className="h-full rounded-full bg-[#C58B2A] transition-[width] duration-300" style={{ width: `${progress}%` }} /></div>
    {assessment.isPending && <div className="mt-12 rounded-xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500" data-testid="assessment-loading-state">Loading your question path…</div>}
    {assessment.isError && <div className="mt-12 rounded-xl border border-rose-200 bg-rose-50 p-6 text-sm text-rose-800" data-testid="assessment-error-state">We couldn’t load the assessment. Your profile is safe—please return and try again.</div>}
    {question && <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_280px]">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8" data-testid="assessment-question-card">
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500"><span className="font-mono font-semibold text-[#A66D12]" data-testid="assessment-question-number">QUESTION {index + 1} / {questionList?.length}</span><span className="rounded-full bg-slate-100 px-3 py-1 font-semibold" data-testid="assessment-question-type">{typeLabels[question.question_type]}</span><span>{question.domain} · Level {question.difficulty}</span></div>
        {question.context && <div className="mt-6 rounded-lg border-l-4 border-[#C58B2A] bg-amber-50 p-4 text-sm leading-6 text-slate-700" data-testid="assessment-question-context">{question.context}</div>}
        <h2 className="mt-7 text-2xl font-bold leading-9 text-slate-900" data-testid="assessment-question-prompt">{question.prompt}</h2>
        <div className="mt-7 space-y-3">{question.options.map((option, optionIndex) => <button key={option} onClick={() => setAnswers((current) => ({ ...current, [question.id]: optionIndex }))} className={`flex w-full items-start gap-3 rounded-lg border p-4 text-left text-sm transition-colors ${answers[question.id] === optionIndex ? "border-[#174A3A] bg-emerald-50 text-[#174A3A]" : "border-slate-200 text-slate-700 hover:border-amber-300 hover:bg-amber-50/50"}`} data-testid={`assessment-option-${optionIndex}`}><span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-current text-xs font-semibold">{String.fromCharCode(65 + optionIndex)}</span>{option}</button>)}</div>
        <div className="mt-8 flex items-center justify-between border-t border-slate-100 pt-5"><button disabled={index === 0} onClick={() => setIndex((current) => current - 1)} className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 disabled:opacity-40" data-testid="assessment-previous-button"><ChevronLeft size={16} />Previous</button>{index === (questionList?.length ?? 1) - 1 ? <button disabled={answered < (questionList?.length ?? 0) || submit.isPending} onClick={() => submit.mutate()} className="inline-flex items-center gap-2 rounded-md bg-[#174A3A] px-5 py-2.5 text-sm font-bold text-white disabled:opacity-50" data-testid="assessment-submit-button">{submit.isPending ? "Saving result…" : "See my result"}<ArrowRight size={16} /></button> : <button disabled={answers[question.id] === undefined} onClick={() => setIndex((current) => current + 1)} className="inline-flex items-center gap-2 rounded-md bg-[#174A3A] px-5 py-2.5 text-sm font-bold text-white disabled:opacity-50" data-testid="assessment-next-button">Next question <ArrowRight size={16} /></button>}</div>
        {submit.isError && <p className="mt-4 text-sm text-rose-700" role="alert" data-testid="assessment-submit-error">We couldn’t save this result. Please review every answer and try again.</p>}
      </section>
      <aside className="rounded-xl border border-amber-200 bg-amber-50 p-6" data-testid="assessment-context-card"><Sparkles size={20} className="text-[#A66D12]" /><p className="mt-5 text-xs font-bold uppercase tracking-[0.14em] text-[#8A570E]">Why this matters</p><h3 className="mt-3 text-lg font-bold text-slate-900">{question.skill}</h3><p className="mt-3 text-sm leading-6 text-slate-600">This answer contributes to your {question.domain.toLowerCase()} readiness, skill-gap analysis and future explainable matches.</p></aside>
    </div>}
  </div></DashboardShell>;
}

function AssessmentResultView({ result }: { result: AssessmentResult }) {
  return <DashboardShell role="student" mode="real"><div className="mx-auto max-w-5xl px-4 py-10 sm:px-8" data-testid="assessment-result-page">
    <p className="font-mono text-xs font-semibold uppercase tracking-[0.17em] text-[#A66D12]">PARIKSHA · RESULT SAVED</p><h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Your career map just got sharper.</h1><p className="mt-3 text-sm leading-6 text-slate-600">This 25-question result is saved to your profile and shapes your next opportunity explanations.</p>
    <div className="mt-8 grid gap-6 lg:grid-cols-[.75fr_1.25fr]"><div className="rounded-xl border border-slate-200 bg-white p-8"><p className="font-mono text-xs uppercase tracking-[0.15em] text-[#A66D12]">READINESS</p><p className="mt-4 font-mono text-7xl font-semibold text-slate-900">{result.readiness}%</p><p className="mt-2 text-sm text-slate-500">Detailed assessment complete</p><Link to="/app/student/skills" className="mt-8 inline-flex items-center gap-2 rounded-md bg-[#174A3A] px-4 py-2.5 text-sm font-bold text-white" data-testid="assessment-result-dashboard-link">View Skill Graph <ArrowRight size={16} /></Link></div><div className="rounded-xl border border-slate-200 bg-white p-6" data-testid="assessment-result-breakdown"><h2 className="text-xl font-bold text-slate-900">Readiness by domain</h2><div className="mt-6 space-y-4">{Object.entries(result.skill_scores).map(([domain, score]) => <div key={domain}><div className="flex justify-between text-sm"><span className="font-medium text-slate-700">{domain}</span><span className="font-mono text-[#174A3A]">{score}%</span></div><div className="mt-2 h-2 rounded-full bg-slate-100"><div className="h-full rounded-full bg-[#C58B2A]" style={{ width: `${score}%` }} /></div></div>)}</div></div></div>
    <div className="mt-6 grid gap-6 lg:grid-cols-2"><div className="rounded-xl border border-amber-200 bg-amber-50 p-6" data-testid="assessment-result-gaps"><p className="font-mono text-xs font-bold uppercase tracking-[0.14em] text-[#8A570E]">SKILL GAPS</p><div className="mt-4 space-y-3">{result.gaps.length ? result.gaps.map((gap) => <p key={gap} className="flex items-center gap-2 text-sm text-amber-950"><Sparkles size={15} className="text-[#A66D12]" />{gap}</p>) : <p className="text-sm text-amber-950">No immediate gaps detected in this pass.</p>}</div></div><div className="rounded-xl border border-slate-200 bg-white p-6" data-testid="assessment-result-recommendations"><p className="font-mono text-xs font-bold uppercase tracking-[0.14em] text-[#A66D12]">NEXT RECOMMENDATIONS</p><div className="mt-4 space-y-3">{result.recommendations.length ? result.recommendations.map((recommendation) => <p key={recommendation} className="flex items-center gap-2 text-sm text-slate-700"><CheckCircle2 size={15} className="text-[#174A3A]" />{recommendation}</p>) : <p className="text-sm text-slate-600">Continue building verified evidence through projects and internship milestones.</p>}</div></div></div>
  </div></DashboardShell>;
}