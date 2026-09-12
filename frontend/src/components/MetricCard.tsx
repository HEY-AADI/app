import { ArrowUpRight } from "lucide-react";

export default function MetricCard({ label, value, note, testId }: { label: string; value: string; note: string; testId: string }) {
  return <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-[0_8px_30px_rgba(15,23,42,.04)]" data-testid={testId}><div className="flex items-center justify-between"><p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500" data-testid={`${testId}-label`}>{label}</p><ArrowUpRight size={16} className="text-amber-600" /></div><p className="mt-3 font-mono text-3xl font-semibold tracking-tight text-[#0B3C2A]" data-testid={`${testId}-value`}>{value}</p><p className="mt-1 text-xs text-slate-500" data-testid={`${testId}-note`}>{note}</p></div>;
}