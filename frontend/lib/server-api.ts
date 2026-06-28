import { cookies } from "next/headers";

// Server Components run inside the frontend container/process, so they must
// reach the backend by its Docker service name, not "localhost".
const SERVER_API_URL =
  process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Fetch wrapper for Server Components: httpOnly cookies aren't forwarded
 * automatically on a server-to-server request, so we read them from the
 * incoming request and attach them manually. Returns null on 401/404 so
 * pages can treat "not logged in" / "not found" as plain data, not an
 * exception. */
export async function serverFetch<T>(path: string, init: RequestInit = {}): Promise<T | null> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();

  const response = await fetch(`${SERVER_API_URL}${path}`, {
    ...init,
    headers: { ...(init.headers as Record<string, string>), Cookie: cookieHeader },
    cache: "no-store",
  });

  if (response.status === 401 || response.status === 404) return null;
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with ${response.status}`);
  }
  return response.json();
}
