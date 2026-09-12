# SAMANVAYA Phase 2 Living Spec

## Product
SAMANVAYA is a government-grade AYUSH academia–industry skill exchange prototype. It is built around one conceptual AYUSH Skill Graph and the loop: Assess → Match → Mentor → Work → Verify → Grow.

## Phase 2 boundary
Authentication, opportunity/application/internship persistence and adaptive Pariksha assessment run through FastAPI + PostgreSQL. Employer verification, credential verification, Ministry data, DigiLocker/APAAR/ABC/ONEST/Beckn/Bhashini and production notifications remain demo or integration-ready.

## Demo personas
- Student: Ananya Sharma, BAMS final year
- Employer: Dabur Research Labs
- Alumni/Mentor: Dr. Rajesh Vaidya
- Institution: National Institute of Ayurveda
- Ministry Officer: Ministry Admin

## Key flows
- Public homepage → opportunities → opportunity detail → explainable match → apply → My Experience / Karma tracker
- Student workspace → Pariksha readiness → Yojana recommendations → Alumni/Mentors → Pramana Career Passport
- Karma shows mentor, defined deliverable, check-in divergence alert, evidence pack preview and credential preview
- Role switcher previews employer, alumni, institution and ministry dashboards with aggregate mock analytics

## Data model
PostgreSQL tables: users, sessions, opportunities, applications, internships, assessment_results and status_checks. Demo fallback data remains in `frontend/src/data/mock.ts` for the public `/demo/*` experience. Auth sessions are random httpOnly cookies with seven-day expiry. Passwords are PBKDF2-SHA256 hashed server-side.

## Auth and roles
Seeded email/password accounts exist for student, employer, alumni/mentor, institution and ministry roles. `/app/*` is protected by server-validated sessions; `/demo/*` remains the clearly labelled mock persona experience.

## Assessment
Pariksha has a 12-question question bank across clinical, AYUSH knowledge, communication, digital, industry and research domains. Submissions compute domain readiness, gaps and recommendations and persist the latest result for the signed-in student.