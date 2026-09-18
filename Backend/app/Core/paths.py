"""Every filesystem path Closet AI uses is resolved here.

There are two very different ways the application can run:

* **From source** — `uv run python main.py` inside `Backend/`. Writable data
  keeps living next to the code (`Backend/closet.db`, `Backend/images`,
  `Backend/logs`) so the existing development workflow is untouched.

* **Packaged** — `ClosetAI.exe` built by PyInstaller. The executable and the
  bundled frontend are read-only (and, in one-file mode, extracted to a
  temporary directory that is deleted on exit), so *all* writable data goes to
  the standard Windows per-user location instead:

      %LOCALAPPDATA%\\ClosetAI\\
          data\\closet.db
          images\\
          logs\\

  `%LOCALAPPDATA%` (and not `%APPDATA%`) is the right choice: roaming profiles
  are meant for small settings that should follow a user between machines, while
  a wardrobe database plus its images are large, machine-local data. This is the
  same location other Windows desktop applications use for user data.

Nothing here ever depends on `os.getcwd()`, so the executable behaves the same
no matter which directory it is launched from.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Closet AI"
APP_ID = "ClosetAI"
APP_VERSION = "0.1.0"

#: Set this to force a specific data directory (handy for tests and for a
#: portable installation on a USB stick).
DATA_DIR_ENV_VAR = "CLOSETAI_DATA_DIR"

#: Set by packaging/launcher.py, so the backend can tell that a desktop
#: window owns this process and may ask it to quit.
DESKTOP_ENV_VAR = "CLOSETAI_DESKTOP"


def is_packaged() -> bool:
    """True when running from a PyInstaller bundle."""
    return bool(getattr(sys, "frozen", False))


def is_desktop_app() -> bool:
    """True when started by the desktop launcher (packaged, or `launcher.py`).

    Only then does the app expose the endpoint the frontend's Quit button uses.
    """
    return is_packaged() or os.environ.get(DESKTOP_ENV_VAR) == "1"


def _meipass() -> Path | None:
    """The temporary directory PyInstaller extracts the bundle into (None in dev)."""
    location = getattr(sys, "_MEIPASS", None)
    return Path(location) if location else None


def bundled_dir() -> Path:
    """Read-only directory holding the bundled application files.

    Packaged: the PyInstaller extraction directory (`sys._MEIPASS`).
    Development: the `Backend/` directory that contains `main.py`.
    """
    if is_packaged():
        return _meipass() or Path(sys.executable).resolve().parent

    # .../Backend/app/Core/paths.py -> .../Backend
    return Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    """Repository root — only meaningful when running from a source checkout."""
    return Path(__file__).resolve().parents[3]


def app_data_dir() -> Path:
    """Writable root for user data (database, images, logs)."""
    override = os.environ.get(DATA_DIR_ENV_VAR)

    if override:
        return Path(override).expanduser().resolve()

    if is_packaged():
        base = os.environ.get("LOCALAPPDATA")

        # LOCALAPPDATA always exists on Windows; fall back for safety.
        root = Path(base) if base else Path.home() / "AppData" / "Local"
        return root / APP_ID

    return bundled_dir()


def database_path() -> Path:
    """SQLite file location.

    Development keeps the historical `Backend/closet.db` so existing local
    databases keep working; packaged builds use `<app data>/data/closet.db`.
    """
    if is_packaged():
        return app_data_dir() / "data" / "closet.db"

    return app_data_dir() / "closet.db"


def images_dir() -> Path:
    """Where uploaded wardrobe images are written (also served as `/images/...`)."""
    return app_data_dir() / "images"


def logs_dir() -> Path:
    """Where log files are written."""
    return app_data_dir() / "logs"


def instance_file() -> Path:
    """Records the port of the running instance, for the single-instance check."""
    return app_data_dir() / "closet-ai.instance"


def frontend_dist_dir() -> Path:
    """The production React build, if it has been built/bundled."""
    if is_packaged():
        return bundled_dir() / "frontend"

    return repo_root() / "Frontend" / "dist"


def ensure_directories() -> None:
    """Create every writable directory the application needs. Safe to call often."""
    for directory in (database_path().parent, images_dir(), logs_dir()):
        directory.mkdir(parents=True, exist_ok=True)


def describe() -> str:
    """Human-readable summary, logged at startup to make support requests easier."""
    mode = "packaged" if is_packaged() else "source"

    return (
        f"mode={mode} app_data={app_data_dir()} "
        f"database={database_path()} images={images_dir()} logs={logs_dir()}"
    )
