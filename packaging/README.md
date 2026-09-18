# Packaging Closet AI for Windows

Everything needed to turn this project into a single `ClosetAI.exe` that a
non-technical Windows user can download, double-click and use — with no Python,
Node.js, `uv` or `pip` anywhere on their machine.

```
Download  →  Double-click  →  Use
```

---

## 1. What a user does

1. Download `ClosetAI-Windows-x64.exe` from the GitHub release page.
2. Double-click it.
3. Closet AI opens in the default browser and the backend starts quietly in the
   background. First launch creates `%LOCALAPPDATA%\ClosetAI`.
4. Create an account, add a Gemini API key in **Settings → API configuration**,
   start adding clothes.
5. Quit with **Settings → Application → Quit Closet AI** when finished. (Or
   sign out and close the browser — the app keeps running until you quit.)

Windows may show a SmartScreen prompt the first time ("Windows protected your
PC"). That is normal for a new, unsigned executable — see
[section 8](#8-smartscreen-smart-app-control-and-antivirus).

### Starting it without holding onto your terminal

`ClosetAI.exe` is built **without a console**, so it never opens a window of its
own and nothing appears on screen except the browser. It is still a normal
long-running program: if you start it from a terminal, that terminal belongs to
it until Closet AI quits, and in a script the command appears to "hang".

Start it detached instead:

```powershell
# PowerShell - returns to the prompt straight away
Start-Process .\ClosetAI.exe

# cmd.exe
start "" ClosetAI.exe
```

```bash
# Git Bash and similar: the & returns the prompt, but note that some tools,
# CI harnesses and agent runtimes still wait for every child process.
# Prefer Explorer or Start-Process in those places.
./ClosetAI.exe &
```

The normal way is simply **double-clicking the file in Explorer**: no window, no
prompt, and the app keeps running quietly in the background until the user quits
it from **Settings → Application → Quit Closet AI**.

For scripts and tests, `CLOSETAI_NO_BROWSER=1` starts the backend without opening
a browser (see [section 6](#6-environment-variables)), and the port it chose is in
`%LOCALAPPDATA%\ClosetAI\closet-ai.instance`.

---

## 2. How to build

From the repository root, in PowerShell:

```powershell
./build_windows.ps1
```

If PowerShell refuses to run the script, either run it as
`powershell -ExecutionPolicy Bypass -File build_windows.ps1`, or allow local
scripts once with `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

The script:

1. runs `npm ci` + `npm run build` in `Frontend/` (skipped with `-SkipFrontend`),
2. runs `uv sync` in `Backend/` (this pulls in PyInstaller from the `dev`
   dependency group),
3. runs PyInstaller against `packaging/ClosetAI.spec` (cached output is cleared
   with `-Clean`),
4. copies the result to `release/`.

Requirements on the **build** machine: Node.js 20+, `uv`, and internet access on
the first build. The resulting executable needs none of them.

### Where the executable ends up

```
release/ClosetAI-Windows-x64.exe      <- the file to publish
packaging/dist/ClosetAI.exe           <- raw PyInstaller output
packaging/build/                      <- PyInstaller work directory (ignored)
```

Building by hand instead of using the script:

```powershell
cd Frontend; npm install; npm run build
cd ..; uv run --project Backend pyinstaller --noconfirm --clean --distpath packaging/dist --workpath packaging/build packaging/ClosetAI.spec
```

---

## 3. What is inside the executable

`packaging/launcher.py` is the entry point, `packaging/ClosetAI.spec` is the
build definition. The launcher:

1. resolves and creates the writable data directory,
2. points logging at `logs/launcher.log` (uvicorn + launcher) — the app's own
   logger writes `logs/closet-ai.log`,
3. checks whether Closet AI is already running and, if so, just re-opens it
   instead of starting a second server,
4. binds a **free loopback port** (`127.0.0.1`, port `0` → the OS picks one), so
   the app never collides with whatever else is on the machine, and never fails
   because "port 8000 is busy",
5. starts uvicorn **in a background thread of the same process** — the user
   never runs `uvicorn` themselves,
6. polls `GET /health` until the API truly answers (up to 60 s) rather than
   sleeping for a fixed time; if the backend dies first, the launcher fails
   immediately with a message box instead of opening a broken page,
7. opens `http://127.0.0.1:<port>/` in the default browser,
8. waits; when the UI calls `POST /app/shutdown` (or the process gets
   Ctrl+C/SIGTERM), it stops uvicorn gracefully, removes the instance file and
   exits.

The backend serves the production frontend itself (`SPAStaticFiles` in
`Backend/main.py`), so the UI, the API and the auth cookies all live on **one
origin** — which is what the `SameSite=Lax` cookies require. Python routes such
as `/login` and `/dashboard` fall back to `index.html` so a page reload works.

The React dev server is never used in the packaged app, and no `.env` file is
required: the frontend talks to its own origin.

### One-file vs one-folder

This project uses **one-file** mode (~27 MB): the bundle extracts itself to a
temporary folder on each launch, which costs roughly a second of startup time
but gives users one clean file to download and move around.

If you would rather have instant startup and can accept shipping a folder, change
`EXE(...)` in `packaging/ClosetAI.spec` into `EXE(...)` + `COLLECT(...)` and pass
`a.binaries, a.datas` to `COLLECT` (see the PyInstaller docs for `EXE`/`COLLECT`),
then ship the resulting folder zipped. Trade-off: faster start, but users must
unzip and keep the whole folder together instead of having a single `.exe`.

### A native window instead of a browser tab

Opening the default browser is deliberate: zero extra dependencies and nothing to
keep in sync. If you later want a real desktop window, the lightest option is
`pywebview` (adds the Windows WebView2 runtime requirement, ~ a few MB): keep
everything else identical and replace `open_app_window()` in `launcher.py` with
`webview.create_window("Closet AI", url)` + `webview.start()`, then set
`should_exit` when the window closes. Electron is not needed and is deliberately
avoided — it would double the download size and add a second runtime.

---

## 4. Where user data lives

| What                | Path                                        |
| ------------------- | ------------------------------------------- |
| SQLite database     | `%LOCALAPPDATA%\ClosetAI\data\closet.db`     |
| Uploaded images     | `%LOCALAPPDATA%\ClosetAI\images\`            |
| Logs                | `%LOCALAPPDATA%\ClosetAI\logs\`              |
| Running port record | `%LOCALAPPDATA%\ClosetAI\closet-ai.instance` |

`%LOCALAPPDATA%` (not `%APPDATA%`) is the Windows-standard home for
machine-local application data: roaming profiles are for small settings that
should follow a user between machines, while a wardrobe database plus its images
can be large. Nothing is written next to the executable, into the PyInstaller
extraction directory, or into any protected installation folder — so the app runs
correctly from any location (Desktop, Downloads, a USB stick) and survives an
upgrade of the executable itself.

All of this is centralised in `Backend/app/Core/paths.py`. Running from source
keeps the historical development layout (`Backend/closet.db`, `Backend/images`,
`Backend/logs`), so existing local databases keep working.

Override the location with the `CLOSETAI_DATA_DIR` environment variable (useful
for tests or a portable install on a USB stick).

---

## 5. API keys

- Users paste their own Gemini (and optional OpenWeather) key into
  **Settings → API configuration**.
- Keys are sent straight to the local backend and stored in the local SQLite
  database (`users.gemini_api_key` / `users.openweather_api_key`) — the existing
  behaviour, unchanged.
- No key is ever hardcoded in the executable, placed in the React build, written
  to `localStorage`/`sessionStorage`, put in a URL, or logged. `packaging/` and
  `Frontend/.env.example` contain no secrets, and nothing in the build pipeline
  copies a `.env` file into the bundle.

---

## 6. Environment variables

None are required at runtime. These exist for development and for support:

| Variable              | Purpose                                                        |
| --------------------- | -------------------------------------------------------------- |
| `CLOSETAI_DATA_DIR`   | Use a different writable data directory                        |
| `CLOSETAI_NO_BROWSER` | `1` = start the backend but do not open a browser (for testing) |
| `CLOSETAI_DESKTOP`    | Set by the launcher; exposes `POST /app/shutdown`               |
| `VITE_API_BASE_URL`   | Frontend build-time API origin (empty = same origin)            |
| `VITE_API_PROXY_TARGET` | Dev-server proxy target (development only)                   |

---

## 7. Testing the build

Test the executable, not the build log — a successful PyInstaller run proves
nothing about whether the app works.

**A quick manual pass** (copy the `.exe` somewhere else first, e.g. the Desktop,
to prove it does not depend on the project folder):

```powershell
$env:CLOSETAI_NO_BROWSER = "1"     # so the test does not open a browser
.\ClosetAI.exe
type "$env:LOCALAPPDATA\ClosetAI\closet-ai.instance"   # the port it chose
curl "http://127.0.0.1:<port>/health"                  # {"status":"ok","desktop":true,...}
```

Then, with the same port:

```powershell
curl.exe -X POST "http://127.0.0.1:<port>/users/" -H "Content-Type: application/json" -d '{\"username\":\"tester\",\"password\":\"pw123456\"}'
curl.exe -c cj.txt -X POST "http://127.0.0.1:<port>/users/login" -H "Content-Type: application/json" -d '{\"username\":\"tester\",\"password\":\"pw123456\"}'
curl.exe -b cj.txt -F "image=@C:\path\to\photo.jpg" -F "name=White Shirt" -F "color=white" -F "clothe_type=top" -F "season=all" -F "formality=casual" "http://127.0.0.1:<port>/clothes/"
```

(The cookie-only call is the interesting one: the backend turns the cookie into
the `?token=` parameter the protected routes expect.)

**Checklist** — all of these were verified for this build:

- [ ] Runs from an arbitrary directory (Desktop, `%TEMP%`, a USB stick).
- [ ] Runs with no Python / Node.js / `uv` / `pip` on `PATH`.
- [ ] First launch creates `data\closet.db`, `images\` and `logs\`.
- [ ] `GET /health` returns `"status":"ok"`, `"desktop":true`.
- [ ] The frontend loads at `/`, and `/login`, `/dashboard`, `/closet`,
      `/settings` all load too (SPA fallback), including after a hard reload.
- [ ] Register, log in, add / edit / delete a clothing item.
- [ ] The uploaded image lands in `%LOCALAPPDATA%\ClosetAI\images` and is served
      back from `/images/<file>`.
- [ ] AI suggestion returns an outfit with a valid Gemini key, and fails
      gracefully (`503`, not a crash) with an invalid one.
- [ ] Double-clicking the `.exe` a second time re-opens the running instance
      instead of starting a second server.
- [ ] Quit from **Settings → Application** stops the process (check Task
      Manager: no `ClosetAI.exe` left) and leaves the data in place.
- [ ] Restarting keeps the account, the clothes and the saved API keys.
- [ ] `Frontend`/`Backend` development commands still work unchanged.

To test the desktop flow without building the executable:

```powershell
uv run --project Backend python packaging/launcher.py
```

---

## 8. SmartScreen, Smart App Control and antivirus

An unsigned executable will get attention from Windows. Expect and prepare for:

- **SmartScreen** ("Windows protected your PC") on first launch for users who
  downloaded the file. They can click *More info → Run anyway*.
- **Smart App Control** (Windows 11, enabled on some machines) refuses to run
  binaries whose reputation it cannot verify, usually with a plain
  "Access is denied". It can allow a build once and block a later, byte-different
  build of the same app. The CodeIntegrity log
  (`Microsoft-Windows-CodeIntegrity/Operational`) shows these blocks.
- Some antivirus engines label PyInstaller one-file bundles heuristically. UPX
  compression is deliberately disabled in the spec because it makes this worse.

The durable fix is a **code-signing certificate** (an OV/EV certificate or
Azure Trusted Signing) and signing the executable in `build_windows.ps1` with
`signtool sign /fd sha256 /tr <timestamp-url> /td sha256 release\ClosetAI-Windows-x64.exe`.
Signed builds avoid SmartScreen warnings and Smart App Control blocks. A signed
installer (Inno Setup / MSIX) is the next step up if you later want Start-menu
entries and clean uninstall.

---

## 9. Publishing a GitHub release

```powershell
./build_windows.ps1 -Clean
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 release/ClosetAI-Windows-x64.exe --title "Closet AI v0.1.0" --notes "Windows build. Download, double-click, use."
```

Or create the release in the GitHub UI and attach
`release/ClosetAI-Windows-x64.exe` as the asset. `release/`, `packaging/build/`
and `packaging/dist/` are gitignored: the executable is a release asset, not a
committed file.

Tell users in the release notes that their wardrobe lives in
`%LOCALAPPDATA%\ClosetAI`, and that upgrading means downloading the new `.exe`
and deleting the old one — the data stays where it is.

---

## 10. Troubleshooting

**Nothing happens when I double-click it.**
Open `%LOCALAPPDATA%\ClosetAI\logs\launcher.log`. If the file does not exist, the
process never started: check Task Manager for a lingering `ClosetAI.exe`, and
check whether Smart App Control or antivirus blocked the file
(section 8). If it does exist, the log names the failure.

**"Closet AI could not start" message box.**
The message includes the path to `logs\launcher.log`, where the full traceback is
written. The usual causes are a blocked executable or a `%LOCALAPPDATA%` folder
that cannot be written to (rare, e.g. a locked-down profile).

**The browser opens but the page cannot reach the backend.**
Look at `logs\launcher.log` for the port, then check
`http://127.0.0.1:<port>/health` in the browser. If that works, the issue is in
the frontend build; if it does not, the backend failed after the readiness check
— the same log will say why.

**The app seems to hang after quitting.**
The launcher waits up to 20 seconds for uvicorn to stop, then exits anyway. If a
`ClosetAI.exe` is still in Task Manager, end it and check `launcher.log` for the
"did not stop within" warning.

**Where did my clothes go?**
`%LOCALAPPDATA%\ClosetAI\data\closet.db` (plus `images\`). Copy that whole folder
to back up or move a wardrobe. Deleting it starts from scratch.

**Ports.** Nothing is hardcoded: the launcher asks Windows for a free port every
launch, so the URL changes between runs. That is why Quit lives in the UI instead
of the user needing to remember a URL.

---

## 11. Development is unaffected

Nothing in this folder runs during normal development.

```powershell
# Backend
cd Backend; uv run python main.py          # http://127.0.0.1:8000

# Frontend (separate terminal)
cd Frontend; npm run dev                   # http://127.0.0.1:5173
```

Development keeps using `Backend/closet.db` and `Backend/images`, the
`?token=`/cookie handling is identical, and `uv run pytest` / `uv sync` keep
working. The only addition to `Backend/pyproject.toml` is PyInstaller in the
`dev` dependency group.
