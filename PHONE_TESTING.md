# Phone testing (PWA + push) without deploying

Use this guide when you want to test the installable PWA and writing reminders on a real phone while still running the app locally on your PC.

## Why a tunnel is required

- Service workers and Web Push need **HTTPS** (or localhost on the same machine).
- Your phone cannot reach `http://localhost:5173` or `http://192.168.x.x:5173` for PWA/push features.
- Use **Cloudflare Tunnel** (`cloudflared`) to expose local ports over HTTPS.

## One-time setup

1. **Install cloudflared** (if not already):
   ```powershell
   winget install Cloudflare.cloudflared
   ```
   If `cloudflared` is not found, open a **new** terminal or use:
   ```powershell
   & "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:8000
   ```

2. **Backend `.env`** — ensure push vars exist (generate keys once with `npx web-push generate-vapid-keys`):
   ```env
   VAPID_PUBLIC_KEY=...
   VAPID_PRIVATE_KEY=...
   VAPID_SUBJECT=mailto:you@example.com
   CRON_SECRET=your-long-random-secret
   ```

3. **Apply migration** [`backend/migrations/003_push_subscriptions.sql`](backend/migrations/003_push_subscriptions.sql) in Supabase.

4. **Vite** is already configured in [`frontend/vite.config.js`](frontend/vite.config.js) to allow `.trycloudflare.com` hosts and `--host`.

## Each testing session

You need **4 terminals**. Tunnel URLs change every time you restart `cloudflared`.

### Terminal 1 — backend

```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Verify: `http://localhost:8000/health`

### Terminal 2 — backend tunnel

```powershell
cloudflared tunnel --url http://localhost:8000
```

Copy the `https://....trycloudflare.com` URL → **backend tunnel URL**.

### Terminal 3 — frontend

Create or update `frontend/.env.local`:

```env
VITE_API_URL=https://YOUR-BACKEND-TUNNEL-URL
```

Start Vite:

```powershell
cd frontend
npm run dev -- --host
```

### Terminal 4 — frontend tunnel

```powershell
cloudflared tunnel --url http://localhost:5173
```

Copy the `https://....trycloudflare.com` URL → **frontend tunnel URL**.

### Update env for OAuth redirects

**`backend/.env`** — set (then restart backend):

```env
FRONTEND_URL=https://YOUR-FRONTEND-TUNNEL-URL
```

**Google Cloud Console** → OAuth client → **Authorized redirect URI**:

```
https://YOUR-BACKEND-TUNNEL-URL/auth/google/callback
```

Restart the backend after changing `FRONTEND_URL`.

## Test on the phone

1. Open the **frontend tunnel URL** in Chrome (Android) or Safari (iOS 16.4+).
2. Sign in with Google.
3. Tap **remind me to write** and allow notifications.
4. **iOS:** Share → **Add to Home Screen**, then open from the home screen icon (required for push).
5. Trigger a test notification from your PC:

   ```powershell
   curl -X POST "https://YOUR-BACKEND-TUNNEL-URL/push/dispatch-reminders" `
     -H "X-Cron-Secret: YOUR_CRON_SECRET"
   ```

6. Tap the notification → should open `/write?today=1`.
7. Save today’s entry → run dispatch again → you should be skipped until tomorrow.

## Quick checks

| Check | URL |
|---|---|
| Backend health | `https://BACKEND-URL/health` |
| VAPID configured | `https://BACKEND-URL/push/vapid-public-key` |
| PWA manifest | DevTools → Application → Manifest (on desktop preview) |

## When you’re done testing

Stop the tunnel processes (`Ctrl+C` in each cloudflared terminal, or kill `cloudflared.exe`).

Revert to normal local dev:

- Delete `frontend/.env.local`, or set `VITE_API_URL=http://localhost:8000`
- Set `FRONTEND_URL=http://localhost:5173` in `backend/.env`
- Restart backend and frontend

## Troubleshooting

| Problem | Fix |
|---|---|
| `Blocked request… not allowed` | Restart `npm run dev -- --host`; vite allows `.trycloudflare.com` |
| Login redirects to localhost | `FRONTEND_URL` must match the **frontend** tunnel URL; restart backend |
| `Push is not configured` | Set `VAPID_*` in `backend/.env` and restart backend |
| Empty `public_key` from API | Multiple stale backends on port 8000 — stop all Python/uvicorn processes, start one backend |
| `cloudflared` not recognized | New terminal, or use full path under `C:\Program Files (x86)\cloudflared\` |
| No notification on iOS | Must use installed PWA from home screen, not a Safari tab |

## Related docs

- Scheduled reminders in production: [`backend/docs/PUSH_CRON.md`](backend/docs/PUSH_CRON.md)
