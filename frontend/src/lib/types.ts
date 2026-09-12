export type Role = "student" | "employer" | "alumni" | "institution" | "ministry";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: Role;
  institution: string | null;
  readiness: number;
}

export interface SessionResponse { user: AuthUser }

export interface PersistedOpportunity {
  id: string;
  type: "Internship" | "Job" | "Project";
  title: string;
  organisation: string;
  location: string;
  system: string;
  mode: "Hybrid" | "On-site" | "Remote";
  stipend: string;
  duration: string;
  match: number;
  skills: string[];
  gaps: string[];
  verified: boolean;
  mentor: string;
  deliverable: string;
  deadline: string;
}

export interface PersistedApplication {
  id: string;
  opportunity_id: string;
  opportunity_title: string;
  organisation: string;
  status: string;
  next_action: string;
  applied_at: string;
}

export interface Milestone { id: string; title: string; detail: string; status: "complete" | "active" | "upcoming"; date: string }
export interface PersistedInternship { id: string; application_id: string; opportunity_title: string; organisation: string; week: number; total_weeks: number; mentor: string; deliverable: string; divergence_alert: boolean; milestones: Milestone[] }

export interface AssessmentQuestion { id: string; prompt: string; domain: string; skill: string; options: string[]; difficulty: number }
export interface AssessmentStart { session_id: string; questions: AssessmentQuestion[] }
export interface AssessmentResult { id: string; readiness: number; skill_scores: Record<string, number>; gaps: string[]; recommendations: string[]; completed_at: string }