# Closet AI — Frontend

A small React + TypeScript + Vite frontend for the existing **Closet AI** FastAPI
backend. It talks to the real API — nothing here is mocked.

```
Login  →  Dashboard  →  see clothes  →  choose an occasion  →  AI outfit  →  manage closet  →  Settings
```

## Requirements

- Node.js 20+
- The FastAPI backend running locally on `http://127.0.0.1:8000`

## Getting started

```bash
cd Frontend
npm install
cp .env.example .env     # optional: the defaults already work
npm run dev
```

Open <http://127.0.0.1:5173>.

Start the backend first (from the `Backend` folder):

```bash
uv run main.py        # or: .venv/Scripts/python main.py  /  py main.py
```

### Scripts

| Command             | What it does                              |
| ------------------- | ----------------------------------------- |
| `npm run dev`       | Vite dev server with the API proxy        |
| `npm run build`     | Type-check, then build to `dist/`         |
| `npm run preview`   | Serve the production build locally        |
| `npm run typecheck` | Type-check only                           |

## How authentication actually works

The backend sets **HTTP-only cookies** on `POST /users/login`:

- `access_token` (15 minutes)
- `refresh_token` (7 days)

JavaScript cannot read either one, and this app never tries to. Three things
follow from that:

1. Every request is sent with `credentials: "include"`, so the browser attaches
   the cookies for us.
2. The app must be served from the **same origin** as the API. The cookies are
   set with `SameSite=Lax`, which browsers only send on same-site requests.
3. A page reload has no way to tell whether a session exists, so on start-up we
   call `POST /users/refresh` once. If it succeeds we are logged in; if not we
   go to `/login`.

`POST /users/refresh` is called again automatically whenever the in-memory
access-token clock (see `src/utils/auth.ts`) is about to run out, and once more
if a request comes back `401`. There is no retry loop: a replayed request is
never allowed to refresh again.

On logout we call `POST /users/logout`, which clears the cookies server-side.

### The `?token=` query parameter

The OpenAPI document shows `query:token*` on every protected endpoint. That
parameter **is the access token** — the backend declares it as
`Depends(verify_access_token)`, where `verify_access_token(token: str)`, so
FastAPI turns it into a required query parameter.

Putting an access token in a URL is not something a browser app should do,
and here it cannot: the token lives in an HTTP-only cookie, so no frontend code
can read it to put it anywhere.

`vite.config.ts` therefore contains a small **compatibility proxy** that runs on
the dev server. It:

- forwards `/users`, `/clothes` and `/images` to the FastAPI server on the same
  origin (so the `SameSite=Lax` cookies are sent at all), and
- reads `access_token` out of the request's `Cookie` header and appends it as the
  `token` query parameter the backend insists on.

The token never reaches frontend JavaScript, and the URL the browser sees has no
`token` in it.

**In production** the same rule has to exist in whatever serves the app. Put the
built `dist/` folder and the API behind one origin (for example nginx or a
FastAPI `StaticFiles` mount) and add the equivalent header rewrite. Pointing
`VITE_API_BASE_URL` at a different origin will not work while the backend uses
`SameSite=Lax` cookies and `allow_origins=["*"]` (a wildcard origin is not valid
for credentialed requests) — fix the backend's CORS/`SameSite` settings rather
than working around them in the browser.

Set `VITE_API_BASE_URL` only if the API lives at a path prefix or a different
same-site origin. It must never contain secrets.

## Project structure

```
src/
├── components/     Navbar, ClothingCard, OccasionSelector, ClothingFormModal,
│                   ConfirmDeleteModal, Modal, Toast
├── pages/          Login (also registration), Dashboard, Closet, Settings
├── services/api.ts Every fetch call lives here
├── types/api.ts    Types mirroring the backend schemas and enum values
├── utils/          auth.ts (in-memory session clock), labels.ts (friendly names)
├── App.tsx         Routing + session bootstrap
├── main.tsx
└── index.css       Tailwind theme tokens
```

## API endpoints used

| Method | Path                     | Purpose                        |
| ------ | ------------------------ | ------------------------------ |
| POST   | `/users/`                | Register                       |
| POST   | `/users/login`           | Log in (sets cookies)          |
| POST   | `/users/refresh`         | Renew the access token         |
| POST   | `/users/logout`          | Log out                        |
| PATCH  | `/users/location`        | Save location                  |
| PATCH  | `/users/api-keys`        | Save Gemini / OpenWeather keys |
| GET    | `/clothes/`              | List clothes                   |
| GET    | `/clothes/{clothe_id}`   | Single item                    |
| POST   | `/clothes/`              | Add (multipart)                |
| PATCH  | `/clothes/{clothe_id}`   | Update (multipart)             |
| DELETE | `/clothes/{clothe_id}`   | Delete                         |
| GET    | `/clothes/ai-suggestion` | AI outfit for an `occasion`    |

## Security notes

- No token, API key or secret is written to `localStorage`, `sessionStorage`,
  a URL or the console.
- API keys are held in React state only long enough to submit them, then the
  input fields are cleared. They are never displayed back.
- Only `VITE_API_BASE_URL` and `VITE_API_PROXY_TARGET` belong in `.env`; both are
  public configuration.
