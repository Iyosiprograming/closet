/**
 * Session bookkeeping for the frontend.
 *
 * The backend keeps the access token and refresh token in HTTP-only cookies, so
 * JavaScript can never read them. All we track here — in memory, for this page
 * load only — is when the current access token stops being valid, so we can
 * refresh *before* a request fails. Nothing is written to localStorage or
 * sessionStorage.
 */

/** Matches `ACCESS_TOKEN_EXPIRE_MINUTES` in Backend/app/Auth/jwt.py (15 min). */
const ACCESS_TOKEN_TTL_MS = 15 * 60 * 1000;

/** Refresh a little early so a request never races the expiry. */
const REFRESH_MARGIN_MS = 30 * 1000;

let accessTokenExpiresAt = 0;

/** Called after a successful login or refresh, since both hand us a fresh token. */
export function markSessionStarted(): void {
  accessTokenExpiresAt = Date.now() + ACCESS_TOKEN_TTL_MS;
}

export function clearSession(): void {
  accessTokenExpiresAt = 0;
}

/** True while we believe the current access token still has life left in it. */
export function sessionIsFresh(): boolean {
  return Date.now() < accessTokenExpiresAt - REFRESH_MARGIN_MS;
}

type SessionExpiredListener = () => void;

let listener: SessionExpiredListener | null = null;

/**
 * Registered once by App.tsx. Fired when the session cannot be recovered and
 * the user has to log in again.
 */
export function setSessionExpiredHandler(next: SessionExpiredListener): void {
  listener = next;
}

export function notifySessionExpired(): void {
  listener?.();
}
