export class ApiError extends Error {
  constructor(status, code, message, details) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export function readCsrfCookie() {
  const entry = document.cookie.split("; ").find((value) => value.startsWith("labtrack_csrf="));
  return entry ? decodeURIComponent(entry.slice("labtrack_csrf=".length)) : "";
}

export async function api(path, { method = "GET", body, signal } = {}) {
  const headers = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (!["GET", "HEAD", "OPTIONS"].includes(method)) headers["X-CSRF-Token"] = readCsrfCookie();
  let response;
  try {
    response = await fetch(`/api${path}`, {
      method, credentials: "same-origin", headers, signal,
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new ApiError(0, "network_error", "No se pudo conectar. Revisa tu conexión e intenta de nuevo.");
  }
  const payload = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(response.status, payload?.code || "http_error",
      payload?.message || "No se pudo completar la solicitud.", payload?.details);
  }
  return payload;
}
