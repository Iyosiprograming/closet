# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build definition for `ClosetAI.exe`.

Build it with `./build_windows.ps1`, or directly:

    uv run --project Backend pyinstaller packaging/ClosetAI.spec

Two things make this bundle work:

* **The frontend build is shipped as data.** `Frontend/dist` is copied into the
  bundle as `frontend/`, which is where `app/Core/paths.py` looks for it when
  frozen. The FastAPI app serves it, so the UI, the API and the auth cookies
  share one origin.
* **Lazy imports are declared explicitly.** uvicorn, SQLAlchemy, pwdlib and
  argon2 all choose modules by name at runtime, which static analysis cannot
  see.
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

SPEC_DIR = Path(SPECPATH).resolve()
REPO_ROOT = SPEC_DIR.parent
BACKEND_DIR = REPO_ROOT / "Backend"
FRONTEND_DIST = REPO_ROOT / "Frontend" / "dist"

if not (FRONTEND_DIST / "index.html").is_file():
    raise SystemExit(
        "Frontend/dist is missing or incomplete.\n"
        "Build it first:  cd Frontend; npm install; npm run build\n"
        "Or simply run ./build_windows.ps1, which does both steps."
    )

hiddenimports = [
    # uvicorn imports its loop, protocol, lifespan and reloading modules by name.
    *collect_submodules("uvicorn"),
    # SQLAlchemy resolves the dialect from the connection URL string.
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.dialects.sqlite.pysqlite",
    # pwdlib selects its hasher implementation by name.
    *collect_submodules("pwdlib"),
    # argon2-cffi: the low-level backend is imported dynamically.
    "argon2",
    "argon2.low_level",
    "_argon2_cffi_bindings",
    "_cffi_backend",
    # FastAPI imports the multipart parser lazily, when a form is first parsed.
    "multipart",
    "python_multipart",
    # Gemini client (used by app/Helper/gemin_api.py).
    *collect_submodules("google.genai"),
]

datas = [
    # The production React build, served by FastAPI.
    (str(FRONTEND_DIST), "frontend"),
]

excludes = [
    # Build-time and development-only packages that would only add weight.
    "pytest",
    "_pytest",
    "iniconfig",
    "pluggy",
    "py",
    # Unused GUI toolkits (the app opens the default browser instead).
    "tkinter",
    "PyQt5",
    "PyQt6",
    "PySide2",
    "PySide6",
    "matplotlib",
    "numpy",
]

a = Analysis(
    [str(SPEC_DIR / "launcher.py")],
    pathex=[str(BACKEND_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ClosetAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX is deliberately off: it can trip Windows Defender and adds little.
    upx=False,
    # No console window: this is a desktop app for non-technical users. Startup
    # failures are reported with a native message box instead (see launcher.py).
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Add packaging/ClosetAI.ico here to give the executable a custom icon.
    icon=None,
)
