export type Role = "student" | "employer" | "alumni" | "institution" | "ministry";

export type Opportunity = {
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
};

export const roleLabels: Record<Role, { label: string; person: string; initials: string }> = {
  student: { label: "Student", person: "Ananya Sharma", initials: "AS" },
  employer: { label: "AYUSH Employer", person: "Dabur Research Labs", initials: "DR" },
  alumni: { label: "Alumni / Mentor", person: "Dr. Rajesh Vaidya", initials: "RV" },
  institution: { label: "Institution", person: "National Institute of Ayurveda", initials: "NI" },
  ministry: { label: "Ministry Officer", person: "Ministry Admin", initials: "MA" },
};

export const opportunities: Opportunity[] = [
  {
    id: "ayurveda-quality",
    type: "Internship",
    title: "Ayurveda Quality Associate",
    organisation: "Arogya Botanicals",
    location: "Pune, Maharashtra",
    system: "Ayurveda",
    mode: "Hybrid",
    stipend: "₹8,000 / month",
    duration: "8 weeks",
    match: 87,
    skills: ["Panchakarma", "Patient communication", "Clinical documentation", "Ayurveda fundamentals", "Hygiene protocols", "Team collaboration", "Basic digital skills"],
    gaps: ["GMP fundamentals", "Quality documentation"],
    verified: true,
    mentor: "Dr. Rahul Mehta",
    deliverable: "Create a documented QA workflow for one selected production process.",
    deadline: "18 Mar 2026",
  },
  {
    id: "panchakarma-clinic",
    type: "Internship",
    title: "Panchakarma Clinical Intern",
    organisation: "Svastha Ayurveda Centre",
    location: "Bengaluru, Karnataka",
    system: "Ayurveda",
    mode: "On-site",
    stipend: "₹10,000 / month",
    duration: "12 weeks",
    match: 81,
    skills: ["Panchakarma", "Patient communication", "Clinical observation", "Documentation"],
    gaps: ["Case presentation", "Digital health records"],
    verified: true,
    mentor: "Dr. Kavya Menon",
    deliverable: "Prepare a supervised patient-care observation portfolio.",
    deadline: "25 Mar 2026",
  },
  {
    id: "digital-ayush",
    type: "Project",
    title: "Digital AYUSH Research Fellow",
    organisation: "Sutradhar Health Systems",
    location: "Remote · India",
    system: "Cross-system",
    mode: "Remote",
    stipend: "₹12,000 / month",
    duration: "10 weeks",
    match: 74,
    skills: ["Research methods", "Healthcare documentation", "Communication", "Data literacy"],
    gaps: ["Evidence synthesis", "Digital health"],
    verified: true,
    mentor: "Meera Iyer",
    deliverable: "Build a structured literature map for an AYUSH care pathway.",
    deadline: "02 Apr 2026",
  },
];

export const alumni = [
  { name: "Dr. Priya Sharma", education: "BAMS · 2023", role: "Clinical Operations Associate", organisation: "Svastha Ayurveda Centre", focus: ["Clinical operations", "Healthcare management"], available: true, sessions: 4, initials: "PS" },
  { name: "Dr. Arjun Nair", education: "BSMS · 2020", role: "Formulation & Quality Lead", organisation: "Sahaja Life Sciences", focus: ["Siddha", "GMP", "Quality assurance"], available: true, sessions: 8, initials: "AN" },
  { name: "Dr. Farah Khan", education: "BUMS · 2019", role: "Public Health Researcher", organisation: "Centre for Integrative Health", focus: ["Unani", "Research", "Public health"], available: false, sessions: 2, initials: "FK" },
];

export const sessions = [
  { category: "Career talk", title: "From BAMS to Healthcare Operations", host: "Dr. Rahul Mehta", detail: "Healthcare Operations Manager · 45 min · Online", interested: 156 },
  { category: "Industry insight", title: "What quality teams look for in fresh graduates", host: "Dr. Arjun Nair", detail: "Formulation & Quality Lead · 60 min · Online", interested: 89 },
  { category: "Career guidance", title: "Building a credible AYUSH career passport", host: "Dr. Priya Sharma", detail: "Clinical Operations Associate · 30 min · Online", interested: 74 },
];

export const metrics = {
  institution: [
    ["Students", "1,248", "+8.4% this year"],
    ["Internships", "184", "61 active now"],
    ["Placement conversion", "72%", "+11% vs last year"],
    ["Active mentors", "64", "18 alumni mentors"],
  ],
  ministry: [
    ["AYUSH students", "2.4M", "Demo aggregate"],
    ["Active employers", "4,860", "Across 412 districts"],
    ["Open opportunities", "12,840", "Internships + roles"],
    ["Verified skills", "86,412", "Evidence-backed"],
  ],
  employer: [
    ["Active opportunities", "8", "+2 this quarter"],
    ["Applications", "124", "18 new this week"],
    ["Shortlisted", "18", "7 interviews planned"],
    ["Internships active", "6", "2 check-ins due"],
  ],
};

export const skillReadiness: Array<[string, number]> = [
  ["Clinical skills", 82],
  ["AYUSH knowledge", 76],
  ["Communication", 69],
  ["Digital skills", 61],
  ["Industry readiness", 54],
];

export const skillDemand: Array<[string, string, number]> = [
  ["Quality assurance", "High", 92],
  ["Panchakarma", "High", 87],
  ["GMP fundamentals", "High", 81],
  ["Clinical operations", "Medium", 64],
  ["Digital health", "Medium", 59],
];

export const navItems = [
  ["Overview", "overview"],
  ["My Skills", "pariksha"],
  ["Opportunities", "opportunities"],
  ["My Experience", "karma"],
  ["Alumni", "alumni"],
  ["Mentors", "mentors"],
  ["Career Passport", "pramana"],
] as const;