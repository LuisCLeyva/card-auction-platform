const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

async function ensureCsrfCookie(): Promise<string> {
  let token = getCookie("csrftoken");
  if (!token) {
    await fetch(`${API_URL}/api/auth/csrf/`, { credentials: "include" });
    token = getCookie("csrftoken");
  }
  return token ?? "";
}

async function rawRequest(path: string, init: RequestInit = {}): Promise<Response> {
  const method = (init.method ?? "GET").toUpperCase();
  const headers: Record<string, string> = { ...(init.headers as Record<string, string>) };

  if (!SAFE_METHODS.has(method)) {
    headers["X-CSRFToken"] = await ensureCsrfCookie();
    if (init.body && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }
  }

  return fetch(`${API_URL}${path}`, { ...init, method, headers, credentials: "include" });
}

function extractMessage(data: unknown): string | undefined {
  if (!data || typeof data !== "object") return undefined;
  const obj = data as Record<string, unknown>;
  if (typeof obj.detail === "string") return obj.detail;
  const firstKey = Object.keys(obj)[0];
  if (!firstKey) return undefined;
  const value = obj[firstKey];
  return Array.isArray(value) ? `${firstKey}: ${value[0]}` : String(value);
}

/** Fetch wrapper for Client Components: attaches the CSRF header on unsafe
 * methods, sends cookies automatically (credentials: "include"), and — if
 * the access token has expired — refreshes it once and retries silently. */
export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response = await rawRequest(path, init);

  if (response.status === 401 && path !== "/api/auth/refresh/") {
    const refreshed = await rawRequest("/api/auth/refresh/", { method: "POST" });
    if (refreshed.ok) {
      response = await rawRequest(path, init);
    }
  }

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ApiError(extractMessage(data) ?? response.statusText, response.status, data);
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}
