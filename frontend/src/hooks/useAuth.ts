import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { AuthUser } from "@/lib/types";

export function useAuth() {
  return useQuery({ queryKey: ["auth", "me"], queryFn: () => apiGet<AuthUser>("/auth/me"), retry: false, staleTime: 60_000 });
}