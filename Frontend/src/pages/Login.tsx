import { useState } from "react";

import { showToast } from "../components/Toast";
import { ApiError, login, registerUser } from "../services/api";

interface LoginProps {
  /** Called after POST /users/login succeeds (the backend has set the cookies). */
  onAuthenticated: () => void;
}

const inputClass =
  "w-full rounded-xl border border-line bg-soft px-4 py-3 text-sm text-ink placeholder:text-muted focus:border-white/25 focus:outline-none";
const labelClass =
  "mb-2 block text-xs uppercase tracking-[0.14em] text-muted";

export default function Login({ onAuthenticated }: LoginProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const isRegistering = mode === "register";

  function switchMode() {
    setMode(isRegistering ? "login" : "register");
    setError(null);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    if (submitting) return;

    const trimmedUsername = username.trim();

    if (!trimmedUsername || !password) {
      setError("Please enter a username and a password.");
      return;
    }

    setError(null);
    setSubmitting(true);

    try {
      if (isRegistering) {
        await registerUser({ username: trimmedUsername, password });
        showToast("Account created. Please log in.");
        setMode("login");
        setPassword("");
      } else {
        await login({ username: trimmedUsername, password });
        showToast("Welcome back.");
        onAuthenticated();
      }
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Something went wrong. Please try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-5 py-12">
      <div className="w-full max-w-sm">
        <p className="text-center font-heading text-xs font-semibold tracking-[0.32em] text-muted">
          CLOSET AI
        </p>

        <div className="mt-8 rounded-2xl border border-line bg-card p-7">
          <h1 className="text-xl font-semibold text-ink">
            {isRegistering ? "Create your account" : "Welcome back"}
          </h1>

          <p className="mt-2 text-sm text-muted">
            {isRegistering
              ? "Start building your wardrobe."
              : "Sign in to your wardrobe."}
          </p>

          <form onSubmit={handleSubmit} className="mt-7 space-y-5">
            <div>
              <label htmlFor="username" className={labelClass}>
                Username
              </label>
              <input
                id="username"
                value={username}
                autoComplete="username"
                onChange={(event) => setUsername(event.target.value)}
                className={inputClass}
              />
            </div>

            <div>
              <label htmlFor="password" className={labelClass}>
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                autoComplete={isRegistering ? "new-password" : "current-password"}
                onChange={(event) => setPassword(event.target.value)}
                className={inputClass}
              />
            </div>

            {error && (
              <p role="alert" className="text-sm text-red-300">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-full bg-accent px-5 py-3 text-sm font-medium text-accent-ink transition-colors hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting
                ? isRegistering
                  ? "Creating account..."
                  : "Signing in..."
                : isRegistering
                  ? "Create account"
                  : "Login"}
            </button>
          </form>
        </div>

        <button
          type="button"
          onClick={switchMode}
          className="mt-6 w-full text-center text-sm text-muted transition-colors hover:text-ink"
        >
          {isRegistering
            ? "Already have an account? Log in"
            : "New here? Create an account"}
        </button>
      </div>
    </main>
  );
}
