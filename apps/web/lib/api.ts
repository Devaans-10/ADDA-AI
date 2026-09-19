export type Provider = "demo" | "bedrock";
export type Agent = "auto" | "coding" | "document" | "search" | "research";
export type Health = {
  status: "ok";
  provider: Provider;
  capabilities: Record<Exclude<Agent, "auto">, boolean>;
};
export type ChatResponse = {
  request_id: string;
  agent: string;
  answer: string;
  provider: Provider;
  activity: { step: string; status: "completed"; detail: string; duration_ms: number }[];
  citations: { title?: string; url?: string; page?: number }[];
};

const baseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

async function request<T>(path: string, timeoutMs: number, init?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${baseUrl}${path}`, {
      ...init,
      signal: AbortSignal.timeout(timeoutMs),
    });
    let payload;
    try {
      payload = JSON.parse(await response.text());
    } catch (error) {
      if (!(error instanceof SyntaxError)) throw error;
      throw new Error(response.ok
        ? "The API returned an unexpected response. Please check the API address and try again."
        : `The API could not complete the request (${response.status}). Please try again.`);
    }
    if (!response.ok) {
      throw new Error(typeof payload?.detail?.message === "string"
        ? payload.detail.message
        : `The request could not be completed (${response.status}). Please try again.`);
    }
    return payload as T;
  } catch (error) {
    if (error instanceof TypeError) throw new Error("Cannot reach the API. Check that the backend is running and its allowed frontend origin matches this site.");
    if (error instanceof DOMException && (error.name === "TimeoutError" || error.name === "AbortError")) {
      throw new Error("The request timed out. Please try again.");
    }
    throw error;
  }
}

export const getHealth = () => request<Health>("/health", 5_000);
export const sendChat = (message: string, agent: Agent, token: string) => request<ChatResponse>("/api/chat", 35_000, {
  method: "POST",
  headers: { "Content-Type": "application/json", ...(token ? { "X-Demo-Token": token } : {}) },
  body: JSON.stringify({ message, agent }),
});
