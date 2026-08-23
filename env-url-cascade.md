# Env URL cascade (prod default, local + tunnel still work)

## Goal

Keep existing `.env` secrets and current URL values untouched. Add a prod-first URL cascade so local, tunnel, and production all work without overwriting each other.

## Current state

- `backend/.env` already has secrets + `FRONTEND_URL=http://localhost:5173`
- `frontend/.env` has `VITE_API_URL=http://localhost:8000`
- `frontend/.env.local` is comments only (tunnel placeholder)
- Code fallbacks are localhost: `backend/app/config.py`, `frontend/src/api/config.js`
- CORS and Google OAuth only trust `FRONTEND_URL` + localhost
- `PHONE_TESTING.md` currently says overwrite those keys, then revert

Confirmed prod hosts:
- Frontend: https://lekha-likhi.vercel.app
- API: https://lekha-likhi-api.onrender.com

## Cascade (first non-empty wins)

```
TUNNEL  →  LOCAL (only if APP_ENV=local)  →  PROD  →  legacy FRONTEND_URL / VITE_API_URL
```

Empty `APP_ENV` / `VITE_APP_ENV` = **prod**. Local is opt-in. Tunnel wins when filled, so phone testing never edits prod or local values.

## Tasks

- [x] Task 1: Confirm prod frontend origin and API origin from Vercel + Render. Write them only into `*_PROD` keys. → Verify: both URLs return 200 (`/` and `/health`)
- [x] Task 2: **Append-only** on existing env files. Do not delete or rewrite secrets or current `FRONTEND_URL` / `VITE_API_URL`.
  - `backend/.env` add: `APP_ENV=`, `FRONTEND_URL_PROD=`, `FRONTEND_URL_LOCAL=http://localhost:5173`, `FRONTEND_URL_TUNNEL=`
  - `frontend/.env` add: `VITE_APP_ENV=`, `VITE_API_URL_PROD=`, `VITE_API_URL_LOCAL=http://localhost:8000`, `VITE_API_URL_TUNNEL=`
  - Create `backend/.env.local` with `APP_ENV=local` (gitignored)
  - Set `VITE_APP_ENV=local` in `frontend/.env.local` without removing the tunnel comments
  - Mirror the same keys in `backend/.env.example` and `frontend/.env.example`
  - → Verify: `git diff` shows only added lines in `.env*`; secret keys unchanged
- [x] Task 3: Backend resolver in `backend/app/config.py`: `frontend_url` property uses the cascade. Load `(".env", ".env.local")` so `.env.local` can pin `APP_ENV` without touching `.env`. → Verify: `APP_ENV=` resolves prod; `APP_ENV=local` resolves localhost; filled `FRONTEND_URL_TUNNEL` wins
- [x] Task 4: CORS in `backend/app/main.py` and `resolve_frontend_url` in `backend/app/routers/google_auth.py` allow every non-empty cascade origin (prod + local + tunnel + existing localhost). → Verify: local login redirect and prod origin both accepted; unknown origin falls back to resolved default
- [x] Task 5: Frontend `getApiUrl()` in `frontend/src/api/config.js` uses the same cascade (`VITE_API_URL_TUNNEL` → local if `VITE_APP_ENV=local` → `VITE_API_URL_PROD` → legacy `VITE_API_URL`). → Verify: `npm run dev` with `VITE_APP_ENV=local` hits `localhost:8000`; empty env / production build hits prod API
- [x] Task 6: Update `PHONE_TESTING.md` to fill `*_TUNNEL` + restart only. Remove “overwrite then revert” steps. → Verify: guide never tells you to change `*_PROD` or `*_LOCAL`

## Done when

- [x] Existing secrets and current `FRONTEND_URL` / `VITE_API_URL` values still present
- [x] No env override → frontend and backend use **prod** URLs
- [x] `APP_ENV=local` + `VITE_APP_ENV=local` → local frontend talks to local backend (login + `/health`)
- [x] Filling tunnel keys only → phone-test URLs, prod/local keys unchanged
- [x] Cascade unit tests pass (`tests/test_url_cascade.py`: 6 passed). Full suite still hits a pre-existing TestClient/httpx mismatch on this machine. `npm run build` passed.

## Notes

- Never commit real `.env` / `.env.local`. Examples only.
- Google Cloud still needs both `http://localhost:8000/auth/google/callback` and the prod callback — that is console config, not an env overwrite.
- Vercel `VITE_API_URL` and Render `FRONTEND_URL` can stay as-is; cascade is for local files. If dashboard vars are set they still win (process env beats files).
- Tests keep `setdefault("FRONTEND_URL", "http://localhost:5173")` so CI does not need prod.
