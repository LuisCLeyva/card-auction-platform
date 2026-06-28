"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "./api";

export interface CurrentUser {
  id: number;
  email: string;
  display_name: string;
  date_joined: string;
}

export function useCurrentUser() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<CurrentUser>("/api/auth/me/")
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  return { user, loading, setUser };
}
