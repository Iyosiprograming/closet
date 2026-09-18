import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
  useNavigate,
} from "react-router-dom";

import Navbar from "./components/Navbar";
import { ToastContainer, showToast } from "./components/Toast";
import Closet from "./pages/Closet";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Settings from "./pages/Settings";
import { logout, refreshToken } from "./services/api";
import { setSessionExpiredHandler } from "./utils/auth";

/**
 * "checking" is the state we start in: the auth cookies are HTTP-only, so the
 * only way to know whether a session exists is to ask the backend to refresh
 * it. POST /users/refresh succeeds when the refresh cookie is still valid.
 */
type SessionState = "checking" | "active" | "signed-out";

function ProtectedLayout({
  session,
  onLogout,
}: {
  session: SessionState;
  onLogout: () => void;
}) {
  if (session === "checking") {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted">Loading your closet...</p>
      </main>
    );
  }

  if (session === "signed-out") {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      <Navbar onLogout={onLogout} />
      <Outlet />
    </>
  );
}

function AppRoutes() {
  const navigate = useNavigate();
  const [session, setSession] = useState<SessionState>("checking");

  // The API layer tells us when the session can no longer be recovered.
  useEffect(() => {
    setSessionExpiredHandler(() => {
      setSession("signed-out");
      showToast("Your session has expired. Please log in again.", "error");
    });
  }, []);

  // Bootstrap: try to restore the session from the refresh cookie.
  useEffect(() => {
    let cancelled = false;

    void refreshToken().then((restored) => {
      if (!cancelled) setSession(restored ? "active" : "signed-out");
    });

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleLogout() {
    try {
      await logout();
    } catch {
      // The cookies may already be gone; local state is cleared either way.
    }

    setSession("signed-out");
    navigate("/login");
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={
          session === "active" ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Login
              onAuthenticated={() => {
                setSession("active");
                navigate("/dashboard");
              }}
            />
          )
        }
      />

      <Route element={<ProtectedLayout session={session} onLogout={handleLogout} />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/closet" element={<Closet />} />
        <Route path="/settings" element={<Settings onLogout={handleLogout} />} />
      </Route>

      <Route
        path="*"
        element={
          <Navigate to={session === "active" ? "/dashboard" : "/login"} replace />
        }
      />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
      <ToastContainer />
    </BrowserRouter>
  );
}
