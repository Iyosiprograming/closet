"""Closet AI API.

This module is the single entry point for both ways of running the app:

* **From source** — `uv run python main.py` starts uvicorn with auto-reload.
* **Packaged** — `packaging/launcher.py` imports `app` from here and runs uvicorn
  itself, on a free localhost port, inside `ClosetAI.exe`.
"""

from urllib.parse import quote

import jwt
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.Core import paths
from app.Core.database import Base, engine
from app.Core.lifecycle import request_shutdown
from app.Core.logger import logger
from app.Routers.clothe_router import router as clothe_router
from app.Routers.user_router import router as user_router


# Database, images and log directories, in the right place for source and
# packaged runs alike (see app/Core/paths.py).
paths.ensure_directories()

IMAGE_DIR = paths.images_dir()


app = FastAPI(title=paths.APP_NAME)


class AccessTokenQueryMiddleware:
    """Mirror the access-token cookie into the `?token=` query parameter.

    Every protected route depends on `verify_access_token(token: str)`, so
    FastAPI declares the access token as a required *query parameter* — yet
    `POST /users/login` hands the token out as an HTTP-only cookie that
    JavaScript is deliberately unable to read. That combination is impossible
    for a browser client to satisfy on its own.

    The cookie stays the source of truth: this middleware copies its value into
    `?token=` when the parameter is absent, so the frontend never has to read,
    store or expose a token. Tokens provided explicitly are left untouched.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            query = scope.get("query_string", b"")

            if b"token=" not in query:
                token = _access_token_from_cookie(scope.get("headers") or [])

                if token:
                    scope = dict(scope)
                    scope["query_string"] = (
                        f"{query.decode('latin-1')}"
                        f"&token={quote(token, safe='')}"
                    ).encode("latin-1")

        await self.app(scope, receive, send)


def _access_token_from_cookie(headers) -> str | None:
    """Pull `access_token` out of the raw Cookie header (no extra dependency)."""
    for name, value in headers:
        if name.lower() != b"cookie":
            continue

        for part in value.decode("latin-1").split(";"):
            key, _, cookie_value = part.strip().partition("=")

            if key == "access_token" and cookie_value:
                return cookie_value

    return None


class SPAStaticFiles(StaticFiles):
    """Serve the built React app, with a fallback to index.html.

    React Router owns paths such as `/login` and `/dashboard`. Those have no
    file on disk, so a direct visit or a page reload must return index.html and
    let the router render the right screen.
    """

    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)

        except StarletteHTTPException as exc:
            if exc.status_code != 404:
                raise

            return await super().get_response("index.html", scope)


# Cookie -> ?token= compatibility layer, described above.
app.add_middleware(AccessTokenQueryMiddleware)


# CORS. Unchanged: it exists for the Vite dev server, which runs on its own
# origin. The packaged app does not need it, because the API serves the
# frontend from the same origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(user_router)
app.include_router(clothe_router)


@app.exception_handler(jwt.PyJWTError)
async def invalid_token_handler(request: Request, exc: jwt.PyJWTError):
    """An expired or malformed token is a 401, not a 500.

    The frontend refreshes the session once and replays the request when it
    sees a 401, so this keeps an expired token recoverable instead of surfacing
    as an unreadable server error.
    """
    logger.info("Rejected a request with an unusable token: %s", exc)

    return JSONResponse(
        status_code=401,
        content={"detail": "Your session has expired. Please log in again."},
    )


@app.get("/health")
def health_endpoint():
    """Readiness probe for the desktop launcher; also used by the frontend."""
    return {
        "status": "ok",
        "app": paths.APP_NAME,
        "version": paths.APP_VERSION,
        "desktop": paths.is_desktop_app(),
    }


if paths.is_desktop_app():

    @app.post("/app/shutdown")
    def shutdown_endpoint():
        """Quit Closet AI from the Settings page (desktop launcher only)."""
        logger.info("Shutdown requested from the frontend")
        request_shutdown()

        return {"message": "Closet AI is shutting down"}


# Serve uploaded images
app.mount(
    "/images",
    StaticFiles(directory=IMAGE_DIR),
    name="images",
)


@app.on_event("startup")
def startup():
    logger.info("Starting application...")

    Base.metadata.create_all(bind=engine)

    logger.info("Database initialized")
    logger.info("Application started successfully")


@app.on_event("shutdown")
def shutdown():
    logger.info("Shutting down application...")
    logger.info("Application stopped")


# In the packaged app the API also serves the production frontend, which keeps
# the browser, the cookies and the API on one origin (the backend sets its auth
# cookies with `SameSite=Lax`, so they are only sent same-site). Mounted last:
# Starlette matches routes in order, so every API path above still wins.
# In development this simply does nothing unless `Frontend/dist` exists.
FRONTEND_DIST = paths.frontend_dist_dir()

if FRONTEND_DIST.is_dir():
    app.mount(
        "/",
        SPAStaticFiles(directory=FRONTEND_DIST, html=True),
        name="frontend",
    )

    logger.info("Serving the frontend build from %s", FRONTEND_DIST)


if __name__ == "__main__":
    # Development server only. The packaged application never runs this: the
    # launcher starts uvicorn itself, without auto-reload, on a free port.
    logger.info("Paths: %s", paths.describe())

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

