"""Closet AI desktop launcher — the entry point of `ClosetAI.exe`.

This is what a user gets when they double-click the executable. It works with
no console window, no Python and no Node.js: PyInstaller has already bundled the
interpreter, the backend and the production frontend.

What it does, in order:

1. Makes sure `sys.stdout`/`sys.stderr` exist (a windowed build has neither).
2. Resolves the writable user-data directory and creates it.
3. Sends everything to `logs/launcher.log` so startup problems are diagnosable.
4. If another copy is already running, re-opens that one and exits.
5. Reserves a free port on 127.0.0.1 by binding the socket itself, then starts
   uvicorn (the FastAPI app) in a background thread on that socket.
6. Polls `GET /health` until the API really answers — never a blind sleep.
7. Opens the app in the default browser.
8. Waits until the user quits from Settings (or sends Ctrl+C / SIGTERM), then
   stops uvicorn, frees the socket and exits cleanly.

It can also be run straight from a source checkout:
`uv run python packaging/launcher.py`.
"""

from __future__ import annotations

import json
import logging
import os
import signal
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from logging.handlers import RotatingFileHandler
from pathlib import Path

#: How long to wait for the API to answer /health before giving up.
READY_TIMEOUT_SECONDS = 60.0

#: How often to re-check while waiting for the API.
READY_POLL_SECONDS = 0.25

#: Per-request timeout for the readiness probe.
HEALTH_TIMEOUT_SECONDS = 1.0

#: How long uvicorn gets to stop gracefully.
SHUTDOWN_TIMEOUT_SECONDS = 20.0

#: Set this to "1" to start the app without opening a browser (used by tests).
NO_BROWSER_ENV_VAR = "CLOSETAI_NO_BROWSER"

log = logging.getLogger("closet_ai.launcher")


def ensure_streams() -> None:
    """A windowed PyInstaller build has no console: stdout/stderr are None."""
    for name in ("stdout", "stderr"):
        if getattr(sys, name, None) is None:
            setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))


def add_backend_to_sys_path() -> None:
    """From a source checkout, make the `app` package and `main` importable."""
    if getattr(sys, "frozen", False):
        return

    backend_dir = Path(__file__).resolve().parents[1] / "Backend"

    if backend_dir.is_dir() and str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))


# Must happen before the backend is imported.
ensure_streams()
add_backend_to_sys_path()

from app.Core import paths  # noqa: E402  (import order is deliberate)
from app.Core import lifecycle  # noqa: E402  (import order is deliberate)


def configure_logging(logs_directory: Path) -> Path:
    """Route the launcher's and uvicorn's messages to a rotating file."""
    log_file = logs_directory / "launcher.log"

    try:
        handler: logging.Handler = RotatingFileHandler(
            log_file,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
    except OSError:
        # Logging must never be the reason the app fails to start.
        handler = logging.NullHandler()

    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    return log_file


def base_url(port: int) -> str:
    return f"http://127.0.0.1:{port}"


def health_payload(port: int) -> dict | None:
    """The parsed /health response, or None when nothing healthy answers."""
    try:
        with urllib.request.urlopen(
            f"{base_url(port)}/health",
            timeout=HEALTH_TIMEOUT_SECONDS,
        ) as response:
            if response.status != 200:
                return None

            return json.loads(response.read().decode("utf-8"))

    except (urllib.error.URLError, OSError, ValueError):
        return None


def is_ready(port: int) -> bool:
    """True when the API answers its readiness probe."""
    payload = health_payload(port)

    return bool(payload) and payload.get("status") == "ok"


def running_instance_port() -> int | None:
    """Port of an already-running Closet AI instance, if there is one.

    Double-clicking the executable twice should bring the user back to the
    instance they already have, not start a second server.
    """
    try:
        recorded = paths.instance_file().read_text(encoding="utf-8").strip()

    except OSError:
        return None

    try:
        port = int(recorded)

    except ValueError:
        return None

    # Only trust the record if Closet AI itself answers there (the port could
    # have been reused by an unrelated application since the last run).
    payload = health_payload(port)

    if payload and payload.get("app") == paths.APP_NAME:
        return port

    return None


def record_instance(port: int) -> None:
    try:
        paths.instance_file().write_text(str(port), encoding="utf-8")

    except OSError:
        log.warning("Could not write the instance file; two copies may be startable.")


def forget_instance(port: int) -> None:
    """Remove the record — but only if it still points at our own port.

    A second copy of the app that just hands over to the running instance must
    not delete that instance's record on its way out.
    """
    try:
        if paths.instance_file().read_text(encoding="utf-8").strip() == str(port):
            paths.instance_file().unlink(missing_ok=True)

    except OSError:
        pass


def open_local_socket() -> tuple[socket.socket, int]:
    """Reserve a free port on the loopback interface.

    Binding the socket ourselves removes the race between "find a free port"
    and "start the server on that port", so the app never fails because
    something else grabbed port 8000.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    sock.bind(("127.0.0.1", 0))

    return sock, sock.getsockname()[1]





def create_server(port: int):
    """Build the uvicorn server for the FastAPI app."""
    import uvicorn

    from main import app

    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        # Keep the logging configuration set up above.
        log_config=None,
        log_level="info",
        # Access logs would write the access token (which travels as a query
        # parameter) into the log file. Not worth it for a localhost app.
        access_log=False,
    )

    return uvicorn.Server(config)


def wait_until_ready(port: int, server_thread: threading.Thread) -> None:
    """Wait for the API to answer /health, failing fast if it dies first."""
    deadline = time.monotonic() + READY_TIMEOUT_SECONDS

    while time.monotonic() < deadline:
        if is_ready(port):
            return

        if not server_thread.is_alive():
            raise RuntimeError(
                "The backend stopped before it finished starting."
            )

        time.sleep(READY_POLL_SECONDS)

    raise TimeoutError(
        f"The backend did not answer on {base_url(port)}/health within "
        f"{READY_TIMEOUT_SECONDS:.0f} seconds."
    )


def open_app_window(port: int) -> None:
    """Open the app in the user's default browser."""
    url = f"{base_url(port)}/"

    if os.environ.get(NO_BROWSER_ENV_VAR) == "1":
        log.info("%s=1, so no browser window was opened. URL: %s", NO_BROWSER_ENV_VAR, url)
        return

    try:
        opened = webbrowser.open(url)

    except Exception:
        opened = False
        log.exception("Opening a browser window failed")

    if not opened:
        log.warning("Could not open a browser automatically.")
        show_dialog(
            "Closet AI is running",
            f"Closet AI could not open your browser automatically.\n\n"
            f"Open this address to use the app:\n{url}",
            error=False,
        )


def wait_for_shutdown(server, server_thread: threading.Thread) -> None:
    """Block until the app is asked to quit, or the backend dies."""
    while not lifecycle.shutdown_requested.wait(READY_POLL_SECONDS):
        if not server_thread.is_alive():
            raise RuntimeError("The backend stopped unexpectedly.")

    log.info("Shutting down the backend...")

    server.should_exit = True
    server_thread.join(timeout=SHUTDOWN_TIMEOUT_SECONDS)

    if server_thread.is_alive():
        log.warning("The backend did not stop within %.0fs.", SHUTDOWN_TIMEOUT_SECONDS)


def install_signal_handlers() -> None:
    """Ctrl+C / SIGTERM / closing the console should stop the app cleanly."""

    def handle(signum, _frame):
        log.info("Received signal %s, shutting down...", signum)
        lifecycle.shutdown_requested.set()

    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        signum = getattr(signal, name, None)

        if signum is None:
            continue

        try:
            signal.signal(signum, handle)

        except (ValueError, OSError):
            # Not the main thread, or unsupported signal: not fatal.
            pass


def show_dialog(title: str, message: str, error: bool = True) -> None:
    """Show a native Windows message box; never assume a console exists."""
    try:
        import ctypes

        # 0x10 = MB_ICONERROR, 0x40 = MB_ICONINFORMATION
        ctypes.windll.user32.MessageBoxW(None, message, title, 0x10 if error else 0x40)
        return

    except Exception:  # pragma: no cover - non-Windows or no GUI available
        pass

    try:
        print(f"{title}: {message}", file=sys.stderr)

    except Exception:
        pass


def startup_failure_message(log_file: Path, exc: BaseException) -> str:
    return (
        f"Closet AI could not start.\n\n"
        f"{type(exc).__name__}: {exc}\n\n"
        f"Details were written to:\n{log_file}\n\n"
        f"Try starting the application once more. If it keeps failing, please "
        f"share that log file."
    )


def run() -> int:
    # Tells the backend that a desktop window is in charge, which is what makes
    # it expose the endpoint behind the frontend's "Quit Closet AI" button.
    os.environ[paths.DESKTOP_ENV_VAR] = "1"

    paths.ensure_directories()

    log_file = configure_logging(paths.logs_dir())

    log.info("=" * 60)
    log.info("Closet AI %s starting up", paths.APP_VERSION)
    log.info("Paths: %s", paths.describe())

    install_signal_handlers()

    server = None
    server_thread: threading.Thread | None = None
    sock: socket.socket | None = None
    owned_port: int | None = None

    try:
        existing_port = running_instance_port()

        if existing_port:
            log.info(
                "Closet AI is already running on port %s; opening it instead.",
                existing_port,
            )
            open_app_window(existing_port)
            return 0

        sock, port = open_local_socket()
        log.info("Reserved %s for the backend", base_url(port))

        server = create_server(port)

        server_thread = threading.Thread(
            target=server.run,
            kwargs={"sockets": [sock]},
            name="closet-ai-api",
            daemon=True,
        )
        server_thread.start()

        wait_until_ready(port, server_thread)

        log.info("Backend ready at %s", base_url(port))
        record_instance(port)
        owned_port = port
        open_app_window(port)

        wait_for_shutdown(server, server_thread)

        return 0

    except BaseException as exc:  # noqa: BLE001 - must never fail silently
        log.exception("Closet AI could not start")
        show_dialog("Closet AI could not start", startup_failure_message(log_file, exc))

        return 1

    finally:
        if owned_port is not None:
            forget_instance(owned_port)

        if server is not None:
            server.should_exit = True

        if server_thread is not None and server_thread.is_alive():
            server_thread.join(timeout=SHUTDOWN_TIMEOUT_SECONDS)

        if sock is not None:
            try:
                sock.close()

            except OSError:
                pass

        log.info("Closet AI stopped")
        logging.shutdown()


if __name__ == "__main__":
    sys.exit(run())
