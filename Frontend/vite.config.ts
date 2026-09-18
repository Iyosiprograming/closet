import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv, type ProxyOptions } from "vite";

/**
 * The FastAPI backend requires an `?token=` query parameter on every protected
 * route, but it issues the access token as an HTTP-only cookie — which
 * JavaScript deliberately cannot read.
 *
 * The dev proxy solves both problems at once:
 *  1. It serves the app and the API from the same origin, so the backend's
 *     `SameSite=Lax` cookies are actually sent (and no CORS special-casing is
 *     needed, which also keeps the browser's security model intact).
 *  2. It copies the access token out of the cookie on the way through and adds
 *     it as the `token` query parameter the backend expects.
 *
 * The token therefore never reaches frontend code. A production deployment
 * needs the same rule in its reverse proxy — see README.md.
 */
function createApiProxy(target: string): ProxyOptions {
  return {
    target,
    changeOrigin: true,
    configure: (proxy) => {
      proxy.on("proxyReq", (proxyReq, req) => {
        const cookieHeader = req.headers.cookie ?? "";
        const match = cookieHeader.match(/(?:^|;\s*)access_token=([^;]+)/);

        if (!match) return;

        const original = new URL(req.url ?? "/", "http://localhost");
        if (original.searchParams.has("token")) return;

        original.searchParams.set("token", decodeURIComponent(match[1]));
        proxyReq.path = `${original.pathname}${original.search}`;
      });
    },
  };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  const target = env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";
  const apiProxy = createApiProxy(target);

  return {
    plugins: [react(), tailwindcss()],
    server: {
      port: 5173,
      proxy: {
        "/users": apiProxy,
        "/clothes": apiProxy,
        // Clothing images are served by the backend as /images/<file>.
        "/images": apiProxy,
      },
    },
  };
});
