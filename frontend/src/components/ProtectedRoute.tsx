import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import type { Role } from "@/lib/types";

export default function ProtectedRoute({ children, role }: { children: ReactNode; role: Role }) {
  const auth = useAuth();
  const location = useLocation();
  if (auth.isPending) return <div className="flex min-h-screen items-center justify-center bg-[#F8FAF6] text-sm font-semibold text-[#0B3C2A]" data-testid="auth-loading-state">Checking your secure session…</div>;
  if (auth.isError || !auth.data) return <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} replace />;
  if (auth.data.role !== role) return <Navigate to={`/app/${auth.data.role}`} replace />;
  return <>{children}</>;
}