import { Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import Opportunities from "@/pages/Opportunities";
import OpportunityDetail from "@/pages/OpportunityDetail";
import Platform from "@/pages/Platform";
import InfoPage from "@/pages/InfoPage";
import Community from "@/pages/Community";
import Login from "@/pages/Login";
import Assessment from "@/pages/Assessment";
import AuthenticatedWorkspace from "@/pages/AuthenticatedWorkspace";
import ProtectedRoute from "@/components/ProtectedRoute";
import StudentProfilePage from "@/pages/StudentProfile";
import SkillGraph from "@/pages/SkillGraph";
import Karma from "@/pages/Karma";

// One <Route> per page in src/pages; BrowserRouter already wraps this in main.tsx.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/opportunities" element={<Opportunities />} />
      <Route path="/opportunities/:id" element={<OpportunityDetail />} />
      <Route path="/alumni" element={<Community mode="alumni" />} />
      <Route path="/mentors" element={<Community mode="mentors" />} />
      <Route path="/app/student" element={<ProtectedRoute role="student"><AuthenticatedWorkspace /></ProtectedRoute>} />
      <Route path="/app/student/pariksha" element={<ProtectedRoute role="student"><Assessment /></ProtectedRoute>} />
      <Route path="/app/student/profile" element={<ProtectedRoute role="student"><StudentProfilePage /></ProtectedRoute>} />
      <Route path="/app/student/skills" element={<ProtectedRoute role="student"><SkillGraph /></ProtectedRoute>} />
      <Route path="/app/student/karma" element={<ProtectedRoute role="student"><Karma /></ProtectedRoute>} />
      <Route path="/app/student/*" element={<ProtectedRoute role="student"><Platform role="student" mode="real" /></ProtectedRoute>} />
      <Route path="/app/employer/*" element={<ProtectedRoute role="employer"><Platform role="employer" mode="real" /></ProtectedRoute>} />
      <Route path="/app/alumni/*" element={<ProtectedRoute role="alumni"><Platform role="alumni" mode="real" /></ProtectedRoute>} />
      <Route path="/app/institution/*" element={<ProtectedRoute role="institution"><Platform role="institution" mode="real" /></ProtectedRoute>} />
      <Route path="/app/ministry/*" element={<ProtectedRoute role="ministry"><Platform role="ministry" mode="real" /></ProtectedRoute>} />
      <Route path="/demo/student/*" element={<Platform role="student" />} />
      <Route path="/demo/employer/*" element={<Platform role="employer" />} />
      <Route path="/demo/alumni/*" element={<Platform role="alumni" />} />
      <Route path="/demo/institution/*" element={<Platform role="institution" />} />
      <Route path="/demo/ministry/*" element={<Platform role="ministry" />} />
      <Route path="/:slug" element={<InfoPage />} />
    </Routes>
  );
}
