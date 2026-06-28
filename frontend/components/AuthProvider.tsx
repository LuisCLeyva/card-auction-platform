"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";
import { AuthContext, type CurrentUser } from "@/lib/auth";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<CurrentUser>("/api/auth/me/")
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}
