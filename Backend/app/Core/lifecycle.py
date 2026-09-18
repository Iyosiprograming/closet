"""Shutdown handshake between the desktop launcher and the FastAPI app.

The packaged application runs the launcher and uvicorn in the same process, so a
simple in-process event is enough: closing the app from the frontend sets the
event, and the launcher then stops uvicorn and exits.
"""

from __future__ import annotations

import threading

#: Set when the application should shut down.
shutdown_requested = threading.Event()


def request_shutdown() -> None:
    """Ask the desktop launcher to stop the server and exit."""
    shutdown_requested.set()
