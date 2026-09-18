import type {
  AddApiKey,
  AddLocation,
  AppStatus,
  Clothe,
  ClotheFormValues,
  LoginUser,
  MessageResponse,
  UserCreate,
  UserCreateResponse,
} from "../types/api";
import {
  clearSession,
  markSessionStarted,
  notifySessionExpired,
  sessionIsFresh,
} from "../utils/auth";

/**
 * Every call to the Closet AI backend goes through this file.
 *
 * Authentication notes
 * --------------------
 * POST /users/login sets `access_token` and `refresh_token` as HTTP-only
 * cookies, so this code never sees them: `credentials: "include"` lets the
 * browser send them for us. The backend also requires an `?token=` query
 * parameter on protected routes; both the cookie and that parameter are wired
 * up by the same-origin dev proxy in `vite.config.ts`. Nothing here ever reads,
 * stores or logs a token.
 *
 * The access token lives 15 minutes. We refresh ahead of that using the
 * in-memory clock in `utils/auth.ts` (the backend raises a raw 500 rather than
 * a 401 when a JWT has expired, so relying on a 401 alone is not reliable).
 * A 401 still triggers one refresh-and-retry, and never more than one, so there
 * is no refresh loop.
 */

/** Empty string means "same origin" (recommended: keeps cookies working). */
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(
  /\/+$/,
  "",
);

/** An error we are happy to show a user. Raw backend bodies never reach the UI. */
export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type RequestOptions = { auth?: boolean } & Omit<RequestInit, "credentials">;

function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

/** Turns FastAPI's `detail` payload into one readable sentence. */
function readableDetail(body: unknown): string | undefined {
  if (!body || typeof body !== "object" || !("detail" in body)) return undefined;

  const detail = (body as { detail: unknown }).detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    const lines = detail
      .map((entry) => {
        const item = entry as { loc?: unknown; msg?: unknown };
        const field = Array.isArray(item.loc)
          ? item.loc.filter((part) => part !== "body" && part !== "query").join(" ")
          : "";
        const message = typeof item.msg === "string" ? item.msg : "is invalid";
        return field ? `${field}: ${message}` : message;
      })
      .filter(Boolean);

    if (lines.length > 0) return lines.join(", ");
  }

  return undefined;
}

function messageForStatus(status: number, detail?: string): string {
  switch (status) {
    case 400:
      return detail ?? "Please check the information you entered.";
    case 401:
      return detail ?? "Your session has expired. Please log in again.";
    case 403:
      return "You don't have permission to do that.";
    case 404:
      return detail ?? "We couldn't find what you were looking for.";
    case 422:
      return detail ?? "Please check the highlighted fields.";
    default:
      return "Something went wrong. Please try again.";
  }
}

async function toResult(response: Response): Promise<unknown> {
  const text = await response.text();
  let body: unknown = null;

  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = null;
    }
  }

  if (response.ok) return body;

  throw new ApiError(
    response.status,
    messageForStatus(response.status, readableDetail(body)),
  );
}

let refreshInFlight: Promise<boolean> | null = null;

/**
 * POST /users/refresh — the refresh token cookie does the authenticating.
 * Returns false when the session cannot be recovered.
 */
export function refreshToken(): Promise<boolean> {
  if (refreshInFlight) return refreshInFlight;

  const attempt = (async () => {
    try {
      const response = await fetch(apiUrl("/users/refresh"), {
        method: "POST",
        credentials: "include",
      });

      await toResult(response);
      markSessionStarted();

      return true;
    } catch {
      clearSession();
      return false;
    }
  })();

  refreshInFlight = attempt;

  void attempt.finally(() => {
    if (refreshInFlight === attempt) refreshInFlight = null;
  });

  return attempt;
}

async function request<T>(
  path: string,
  options: RequestOptions = {},
  isRetry = false,
): Promise<T> {
  const { auth = true, ...init } = options;

  if (auth && !(await ensureSession())) {
    notifySessionExpired();
    throw new ApiError(401, "Your session has expired. Please log in again.");
  }

  let response: Response;

  try {
    response = await fetch(apiUrl(path), {
      credentials: "include",
      ...init,
    });
  } catch {
    throw new ApiError(
      0,
      "We couldn't reach the server. Please check your connection and try again.",
    );
  }

  if (auth && response.status === 401 && !isRetry) {
    // One refresh, one replay — never more.
    if (await refreshToken()) return request<T>(path, options, true);

    notifySessionExpired();
    throw new ApiError(401, "Your session has expired. Please log in again.");
  }

  return (await toResult(response)) as T;
}

async function ensureSession(): Promise<boolean> {
  if (sessionIsFresh()) return true;
  return refreshToken();
}

function jsonRequest(body: unknown): RequestInit {
  return {
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}

/* -------------------------------------------------------------- application */

/**
 * GET /health — how the app is running. Unauthenticated, and safe to call
 * before there is a session.
 */
export function getAppStatus(): Promise<AppStatus> {
  return request<AppStatus>("/health", { auth: false });
}

/**
 * POST /app/shutdown — asks the packaged desktop app to close.
 *
 * Only the Windows build exposes this route, and only the launcher can act on
 * it; the browser itself never gets to start or stop the server.
 */
export function quitApp(): Promise<MessageResponse> {
  return request<MessageResponse>("/app/shutdown", {
    method: "POST",
    auth: false,
  });
}

/* ------------------------------------------------------------------ users */

/** POST /users/ — registration. Does not log the user in; the backend just returns the new user. */
export function registerUser(
  payload: UserCreate,
): Promise<UserCreateResponse> {
  return request<UserCreateResponse>("/users/", {
    method: "POST",
    auth: false,
    ...jsonRequest(payload),
  });
}

/** POST /users/login — sets the auth cookies on success. */
export async function login(payload: LoginUser): Promise<MessageResponse> {
  const result = await request<MessageResponse>("/users/login", {
    method: "POST",
    auth: false,
    ...jsonRequest(payload),
  });

  markSessionStarted();

  return result;
}

/** POST /users/logout — clears the auth cookies; local session state is reset too. */
export async function logout(): Promise<void> {
  try {
    await request<MessageResponse>("/users/logout", {
      method: "POST",
      auth: false,
    });
  } finally {
    clearSession();
  }
}

/** PATCH /users/location */
export function saveLocation(payload: AddLocation): Promise<MessageResponse> {
  return request<MessageResponse>("/users/location", {
    method: "PATCH",
    ...jsonRequest(payload),
  });
}

/**
 * PATCH /users/api-keys
 * The keys are passed straight through and never stored or logged.
 */
export function saveApiKeys(payload: AddApiKey): Promise<MessageResponse> {
  return request<MessageResponse>("/users/api-keys", {
    method: "PATCH",
    ...jsonRequest(payload),
  });
}

/* ---------------------------------------------------------------- clothes */

/** GET /clothes/ */
export function getClothes(): Promise<Clothe[]> {
  return request<Clothe[]>("/clothes/");
}

/** GET /clothes/{clothe_id} */
export function getClothe(clotheId: number): Promise<Clothe> {
  return request<Clothe>(`/clothes/${clotheId}`);
}

/** GET /clothes/ai-suggestion?occasion=... — returns the clothes the AI picked. */
export function getAiSuggestion(occasion: string): Promise<Clothe[]> {
  return request<Clothe[]>(
    `/clothes/ai-suggestion?occasion=${encodeURIComponent(occasion)}`,
  );
}

/**
 * POST /clothes/ — multipart form data.
 * Content-Type is deliberately not set: the browser adds the multipart
 * boundary itself.
 */
export function createClothe(values: ClotheFormValues): Promise<Clothe> {
  const form = new FormData();

  form.append("name", values.name);
  form.append("color", values.color);
  form.append("clothe_type", values.clothe_type);
  form.append("season", values.season);
  form.append("formality", values.formality);

  if (values.image) form.append("image", values.image);

  return request<Clothe>("/clothes/", { method: "POST", body: form });
}

/**
 * PATCH /clothes/{clothe_id} — multipart form data.
 * Only the fields that changed are appended, so untouched values are left alone.
 */
export function updateClothe(
  clotheId: number,
  changes: Partial<ClotheFormValues>,
): Promise<Clothe> {
  const form = new FormData();

  if (changes.name) form.append("name", changes.name);
  if (changes.color) form.append("color", changes.color);
  if (changes.clothe_type) form.append("clothe_type", changes.clothe_type);
  if (changes.season) form.append("season", changes.season);
  if (changes.formality) form.append("formality", changes.formality);
  if (changes.image) form.append("image", changes.image);

  return request<Clothe>(`/clothes/${clotheId}`, {
    method: "PATCH",
    body: form,
  });
}

/** DELETE /clothes/{clothe_id} */
export function deleteClothe(clotheId: number): Promise<MessageResponse> {
  return request<MessageResponse>(`/clothes/${clotheId}`, { method: "DELETE" });
}

/**
 * The backend stores images itself and returns paths like "/images/<uuid>.jpg".
 * Relative paths are resolved against the API origin.
 */
export function resolveImageUrl(imageUrl: string): string {
  if (!imageUrl) return "";
  if (/^https?:\/\//i.test(imageUrl)) return imageUrl;

  return `${API_BASE_URL}${imageUrl.startsWith("/") ? "" : "/"}${imageUrl}`;
}
