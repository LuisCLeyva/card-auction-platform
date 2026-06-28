import { apiFetch } from "./api";

function mockResponse(status: number, body: unknown = null) {
  return {
    status,
    ok: status >= 200 && status < 300,
    statusText: "error",
    json: async () => body,
  } as unknown as Response;
}

describe("apiFetch", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=test-csrf-token";
    global.fetch = jest.fn();
  });

  afterEach(() => {
    document.cookie = "csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 UTC";
    jest.resetAllMocks();
  });

  it("sends the X-CSRFToken header on unsafe methods", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse(200, { ok: true }));

    await apiFetch("/api/inventory/", { method: "POST", body: JSON.stringify({}) });

    const [, init] = (global.fetch as jest.Mock).mock.calls[0];
    expect(init.headers["X-CSRFToken"]).toBe("test-csrf-token");
  });

  it("does not attach a CSRF header for GET requests", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse(200, { ok: true }));

    await apiFetch("/api/cards/");

    const [, init] = (global.fetch as jest.Mock).mock.calls[0];
    expect(init.headers["X-CSRFToken"]).toBeUndefined();
  });

  it("retries once after a silent refresh on 401", async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce(mockResponse(401))
      .mockResolvedValueOnce(mockResponse(200)) // refresh call
      .mockResolvedValueOnce(mockResponse(200, { id: 1 }));

    const data = await apiFetch<{ id: number }>("/api/auth/me/");

    expect(global.fetch).toHaveBeenCalledTimes(3);
    expect(data).toEqual({ id: 1 });
  });

  it("throws with the server-provided detail message on error", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse(400, { detail: "Nope" }));

    await expect(apiFetch("/api/cards/")).rejects.toThrow("Nope");
  });
});
