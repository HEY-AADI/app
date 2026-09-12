import { Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import Opportunities from "@/pages/Opportunities";
import OpportunityDetail from "@/pages/OpportunityDetail";
import Platform from "@/pages/Platform";
import InfoPage from "@/pages/InfoPage";
import Community from "@/pages/Community";

// One <Route> per page in src/pages; BrowserRouter already wraps this in main.tsx.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/opportunities" element={<Opportunities />} />
      <Route path="/opportunities/:id" element={<OpportunityDetail />} />
      <Route path="/alumni" element={<Community mode="alumni" />} />
      <Route path="/mentors" element={<Community mode="mentors" />} />
      <Route path="/app/student/*" element={<Platform role="student" />} />
      <Route path="/app/employer/*" element={<Platform role="employer" />} />
      <Route path="/app/alumni/*" element={<Platform role="alumni" />} />
      <Route path="/app/institution/*" element={<Platform role="institution" />} />
      <Route path="/app/ministry/*" element={<Platform role="ministry" />} />
      <Route path="/:slug" element={<InfoPage />} />
    </Routes>
  );
}
