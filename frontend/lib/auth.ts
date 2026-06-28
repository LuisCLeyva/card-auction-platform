"use client";

import { createContext, useContext, useEffect, useState } from "react";

import { apiFetch } from "./api";

export interface CurrentUser {
  id: number;
  email: string;
  display_name: string;
  date_joined: string;
}

interface AuthContextValue {
  user: CurrentUser | null;
  loading: boolean;
  setUser: (user: CurrentUser | null) => void;
}

export const AuthContext = createContext<AuthContextValue>({
  user: null,
  loading: true,
  setUser: () => {},
});

export function useCurrentUser() {
  return useContext(AuthContext);
}
