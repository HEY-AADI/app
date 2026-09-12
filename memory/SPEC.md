# SAMANVAYA Phase 1 Living Spec

## Product
SAMANVAYA is a government-grade AYUSH academia–industry skill exchange prototype. It is built around one conceptual AYUSH Skill Graph and the loop: Assess → Match → Mentor → Work → Verify → Grow.

## Phase 1 boundary
The current build is a frontend-only demo with mock data. Authentication, persistence, employer verification, credential verification, analytics, Ministry data, DigiLocker/APAAR/ABC/ONEST/Beckn/Bhashini and real submissions are not connected. These are marked demo or integration-ready in the UI.

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
Mock frontend data in `frontend/src/data/mock.ts` includes opportunities, alumni, sessions, role personas, skill readiness, demand signals and dashboard metrics. Backend remains on the template status endpoints for infrastructure smoke testing.

## Auth and roles
No login is implemented in Phase 1. Demo persona selection is a UI-only role switcher. Real role-based sessions are Phase 2 dependencies.