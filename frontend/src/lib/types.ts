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
  eligibility: string;
  accessibility: string;
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

export type QuestionType = "mcq" | "assertion_reasoning" | "case_based" | "scenario_based";
export interface AssessmentQuestion { id: string; prompt: string; domain: string; skill: string; options: string[]; difficulty: number; question_type: QuestionType; context: string | null }
export interface AssessmentStart { session_id: string; questions: AssessmentQuestion[] }
export interface AssessmentResult { id: string; readiness: number; skill_scores: Record<string, number>; gaps: string[]; recommendations: string[]; completed_at: string }

export type SkillProvenance = "Self-declared" | "Institution verified" | "Employer verified" | "Issuer verified";
export interface SkillEntry { name: string; level: number; provenance: SkillProvenance; evidence: string }
export interface PortfolioEvidence { title: string; issuer: string; evidence_type: "Project" | "Internship" | "Certification" | "Assessment"; date: string }
export interface StudentProfile {
  user_id: string;
  name: string;
  email: string;
  institution: string | null;
  education: string;
  ayush_system: "Ayurveda" | "Siddha" | "Unani" | "Homoeopathy" | "Yoga & Naturopathy";
  graduation_year: number;
  interests: string[];
  skills: SkillEntry[];
  portfolio_evidence: PortfolioEvidence[];
  updated_at: string;
}
export type StudentProfileUpdate = Omit<StudentProfile, "user_id" | "name" | "email" | "institution" | "updated_at">;

export interface CheckIn { id: string; internship_id: string; week: number; actor: "student" | "mentor"; meeting_frequency: "Never" | "Once" | "Weekly"; useful_feedback: "Yes" | "Partially" | "No"; reflection: string; created_at: string }
export interface CheckInSummary { internship_id: string; week: number; student: CheckIn | null; mentor: CheckIn | null; divergence_alert: boolean }
export interface EvidencePack { internship_id: string; opportunity_title: string; organisation: string; deliverable: string; performance_metric: string; mentor_assessment: string; student_reflection: string; completion_status: string; generated_at: string }

export interface CareerPassportDocument { filename: string; media_type: string; content_base64: string }

export interface EmployerOpportunityCreate {
  type: "Internship" | "Job" | "Project";
  title: string;
  system: string;
  skills: string[];
  eligibility: string;
  stipend: string;
  location: string;
  mode: "Hybrid" | "On-site" | "Remote";
  duration: string;
  mentor: string;
  deliverable: string;
  accessibility: string;
  deadline: string;
}
export interface EmployerOpportunity extends EmployerOpportunityCreate { id: string; organisation: string; publication_status: "draft" | "published"; application_count: number }
export interface EmployerCandidate { application_id: string; opportunity_id: string; candidate_code: string; status: "Applied" | "Under Review" | "Shortlisted" | "Interview" | "Selected" | "Rejected" | "Joined" | "Completed"; readiness: number; skills: SkillEntry[]; evidence_count: number; name: string | null; email: string | null; institution: string | null; identity_revealed: boolean; institution_revealed: boolean }