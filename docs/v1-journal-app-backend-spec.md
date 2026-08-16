# Journal App — Backend Specification

> **Goal:** A FastAPI backend for a small-scale, invite-based digital journal app where owners write date-based plain-text entries styled as an old handwritten paper, and can share individual entries via revocable links to Google-authenticated viewers who can react with emoji.

**Architecture:** FastAPI service as the sole business-logic layer, backed by Supabase (Postgres + Google OAuth) for data and identity, and Upstash Redis for share-link caching and reaction rate-limiting. FastAPI enforces all authorization — Supabase RLS is a defense-in-depth backstop only, not the primary access control.

**Tech Stack:** FastAPI, Supabase (Postgres + Auth), Upstash Redis (REST API), Pydantic v2, `httpx` for token verification, `python-jose` or Supabase's JWT verification, React frontend (separate spec).

---

## 1. Requirements

### 1.1 Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | Users authenticate via Google OAuth (through Supabase Auth) — same flow for owners and viewers |
| FR-2 | An authenticated user can create exactly one entry per calendar date (their own entries only) |
| FR-3 | An authenticated user can edit or delete their own entries at any time |
| FR-4 | An owner can list/browse their own entries by date |
| FR-5 | An owner can generate a share link for one specific entry |
| FR-6 | An owner can view all their active/revoked share links in one place |
| FR-7 | An owner can revoke a share link at any time, immediately invalidating it |
| FR-8 | A viewer with a valid, active share link and a Google login can view that single entry |
| FR-9 | A viewer can react to a shared entry with exactly one emoji from a fixed allowed set |
| FR-10 | A viewer can change their reaction (not add multiple) |
| FR-11 | Anyone viewing a shared entry can see all reactions with the reacting user's display name |
| FR-12 | Revoked or non-existent share links return a clear "not available" response, not a data leak |

### 1.2 Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Scale | Tens of users, low request volume (no horizontal scaling needed) |
| Performance | Shared-entry page load should resolve in <300ms server-side (cache-assisted) |
| Security | All entry data private by default; only reachable via active share link + auth. Share tokens are cryptographically random (≥128 bits), unguessable. |
| Privacy | Viewers only ever see the single entry they were given a link to — never other entries, never other owners' data |
| Reliability | Single-region deployment acceptable; no HA requirement for v1 |
| Rate limiting | Reaction endpoint rate-limited per user per entry (e.g., 10 req/min) via Upstash to prevent abuse/spam-clicking |
| Ownership | Solo/small-team maintained; prioritize code clarity over exotic optimization |

### 1.3 Explicit Non-Goals (v1)
- No rich text formatting
- No image attachments
- No comments (emoji reactions only)
- No email/push notifications
- No multi-entry ("whole journal") sharing
- No anonymous (non-authenticated) viewing

---

## 2. Data Model (Postgres via Supabase)

```sql
create table users (
  id uuid primary key references auth.users(id),
  email text not null,
  display_name text not null,
  avatar_url text,
  created_at timestamptz not null default now()
);

create table entries (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references users(id) on delete cascade,
  entry_date date not null,
  body text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner_id, entry_date)
);

create table share_links (
  id uuid primary key default gen_random_uuid(),
  entry_id uuid not null references entries(id) on delete cascade,
  token text not null unique,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  revoked_at timestamptz
);

create table reactions (
  id uuid primary key default gen_random_uuid(),
  entry_id uuid not null references entries(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  emoji text not null,
  created_at timestamptz not null default now(),
  unique (entry_id, user_id)
);
```

**Allowed emoji set** (enforced in app code, not DB): `["❤️", "😢", "👏", "😂", "😮"]`

**Indexes:**
```sql
create index idx_entries_owner_date on entries (owner_id, entry_date desc);
create index idx_share_links_token on share_links (token) where is_active = true;
create index idx_reactions_entry on reactions (entry_id);
```

---

## 3. Authentication & Authorization

### 3.1 Flow
1. Frontend uses Supabase JS client to run Google OAuth; Supabase returns a JWT (access token).
2. Frontend sends this JWT as `Authorization: Bearer <token>` on every FastAPI request.
3. FastAPI verifies the JWT signature against Supabase's JWKS endpoint (cached in memory) and extracts `user_id`, `email`.
4. On first-ever verified login, FastAPI upserts a row into `users` (display_name/avatar from the JWT's user metadata).

### 3.2 Authorization rules (enforced in FastAPI, not just RLS)
- **Entry CRUD**: only `entries.owner_id == current_user.id`.
- **Share link creation/revocation**: only the entry's owner.
- **Viewing a shared entry**: any authenticated user, provided the token maps to an `is_active = true` share link. No ownership check — this is intentionally the "public within your Google identity" access point.
- **Reacting**: any authenticated user who can view the entry (i.e., reached it via a valid share link) — reaction endpoint re-validates the token, does not trust a cached "I already saw this entry" client state.

---

## 4. API Endpoints

### 4.1 Auth/User
```
GET  /me
  → returns current user's profile (upserts on first call)
```

### 4.2 Entries (owner-only)
```
GET    /entries?from=YYYY-MM-DD&to=YYYY-MM-DD
  → list current user's entries in date range, paginated

GET    /entries/{entry_date}
  → get current user's entry for a specific date (404 if none)

PUT    /entries/{entry_date}
  → create or update current user's entry for that date (upsert)
  body: { "body": "plain text..." }

DELETE /entries/{entry_date}
  → delete current user's entry for that date
```

### 4.3 Share Links (owner-only)
```
POST   /entries/{entry_id}/share
  → create a new active share link for this entry, returns { token, url }

GET    /share-links
  → list all share links owned by current user (across all entries),
    with entry_date, is_active, created_at for management UI

DELETE /share-links/{token}
  → revoke (is_active = false) — owner-only, must own the underlying entry
```

### 4.4 Shared View (viewer-facing, requires auth but not ownership)
```
GET    /shared/{token}
  → if token invalid/revoked: 404 "This entry is no longer available"
  → else: returns entry body, entry_date, owner display_name,
    and full reaction list [{ user_display_name, emoji }]

POST   /shared/{token}/react
  → body: { "emoji": "❤️" }
  → validates emoji is in allowed set
  → upserts reaction (entry_id, current_user.id) — changing prior reaction if any
  → rate-limited via Upstash (10/min per user per entry)

DELETE /shared/{token}/react
  → removes current user's reaction from this entry
```

---

## 5. Caching & Rate Limiting (Upstash Redis)

- **Share-link resolution cache**: `share_link:{token}` → `{entry_id, is_active}`, TTL 5 min. On `DELETE /share-links/{token}`, explicitly invalidate this key (don't rely on TTL alone) so revocation is immediate.
- **Reaction rate limit**: sliding-window counter key `ratelimit:react:{user_id}:{entry_id}`, 10 requests/60s, using Upstash's built-in rate-limit SDK (`@upstash/ratelimit` has a Python-compatible REST equivalent, or implement via `INCR` + `EXPIRE`).

---

## 6. Error Handling Conventions

| Situation | Response |
|-----------|----------|
| Invalid/expired JWT | 401 `{"detail": "Not authenticated"}` |
| Accessing another user's entry directly | 404 (not 403 — avoid confirming existence) |
| Revoked/unknown share token | 404 `{"detail": "This entry is no longer available"}` |
| Duplicate entry for same date via race condition | 409, caught from unique constraint violation |
| Invalid emoji | 422 with allowed list in error detail |
| Rate limit exceeded | 429 `{"detail": "Too many reactions, try again shortly"}` |

---

## 7. Implementation Tasks

### Task 1: Project scaffolding
**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/config.py` (env vars: `SUPABASE_URL`, `SUPABASE_JWT_SECRET`, `UPSTASH_REDIS_URL`, `UPSTASH_REDIS_TOKEN`)
- Create: `backend/requirements.txt` (`fastapi`, `uvicorn`, `supabase`, `python-jose[cryptography]`, `httpx`, `pydantic-settings`)
- Create: `backend/app/db.py` (Supabase client init)

Steps:
1. Scaffold FastAPI app with a `/health` endpoint.
2. Wire up `pydantic-settings` to load env vars.
3. Verify `uvicorn app.main:app --reload` boots and `/health` returns 200.
4. Commit.

### Task 2: Auth middleware
**Files:**
- Create: `backend/app/auth.py`
- Test: `backend/tests/test_auth.py`

Steps:
1. Write a `get_current_user` FastAPI dependency that extracts the Bearer token, verifies it against Supabase's JWKS, and returns a `User` pydantic model.
2. Write a failing test asserting a request without a token gets 401.
3. Implement until test passes.
4. Add `/me` endpoint using the dependency; test it upserts a `users` row on first call (mock the Supabase client).
5. Commit.

### Task 3: Entries CRUD
**Files:**
- Create: `backend/app/routers/entries.py`
- Create: `backend/app/schemas/entry.py`
- Test: `backend/tests/test_entries.py`

Steps:
1. Write failing tests for: create entry, get entry by date, update (upsert) entry, delete entry, and — critically — a test that user A cannot fetch user B's entry by date (expect 404).
2. Implement the four endpoints per section 4.2, enforcing `owner_id = current_user.id` on every query.
3. Run tests, confirm pass.
4. Commit.

### Task 4: Share link creation & management
**Files:**
- Create: `backend/app/routers/share_links.py`
- Create: `backend/app/schemas/share_link.py`
- Modify: `backend/app/db.py` (add token generation helper using `secrets.token_urlsafe(32)`)
- Test: `backend/tests/test_share_links.py`

Steps:
1. Write failing tests: create share link for own entry (success), create for someone else's entry (403/404), list own share links, revoke own link, revoke someone else's link (should fail).
2. Implement `POST /entries/{entry_id}/share`, `GET /share-links`, `DELETE /share-links/{token}`.
3. On revoke, ensure the Upstash cache key `share_link:{token}` is deleted (stub Upstash client in tests).
4. Run tests, confirm pass.
5. Commit.

### Task 5: Shared viewer endpoint
**Files:**
- Create: `backend/app/routers/shared.py`
- Test: `backend/tests/test_shared_view.py`

Steps:
1. Write failing tests: valid active token returns entry + reactions; revoked token returns 404; nonexistent token returns 404.
2. Implement `GET /shared/{token}`: check Upstash cache first, fall back to DB, populate cache on miss.
3. Ensure the response includes the entry owner's `display_name` and a `reactions` array with `{display_name, emoji}` per FR-11.
4. Run tests, confirm pass.
5. Commit.

### Task 6: Reactions
**Files:**
- Modify: `backend/app/routers/shared.py`
- Create: `backend/app/services/rate_limit.py`
- Test: `backend/tests/test_reactions.py`

Steps:
1. Write failing tests: react with valid emoji (creates row), react again with different emoji (updates, not duplicates — check unique constraint), react with invalid emoji (422), remove reaction (DELETE), exceed rate limit (429, mock Upstash counter).
2. Implement `POST /shared/{token}/react` and `DELETE /shared/{token}/react`, wiring in the rate-limit service.
3. Run tests, confirm pass.
4. Commit.

### Task 7: Row-Level Security backstop (defense-in-depth)
**Files:**
- Create: `backend/migrations/002_rls_policies.sql`

Steps:
1. Enable RLS on all four tables.
2. Add policy: users can `select`/`update`/`delete` only their own `entries` rows (even though FastAPI already enforces this — belt and suspenders in case the service role key is ever misused).
3. Add policy: `reactions` insertable only by the authenticated user for their own `user_id`.
4. Apply migration to Supabase project, verify via Supabase dashboard.
5. Commit.

### Task 8: Error handling & polish
**Files:**
- Create: `backend/app/exceptions.py` (custom exception handlers per section 6)
- Modify: `backend/app/main.py` (register handlers)
- Test: `backend/tests/test_error_responses.py`

Steps:
1. Write tests asserting each error case in section 6 returns the correct status + shape.
2. Implement exception handlers.
3. Run full test suite, confirm all pass.
4. Commit.

---

## 8. Decision Log

| Decision | Alternatives Considered | Why Chosen |
|----------|--------------------------|------------|
| FastAPI owns authorization, not just Supabase RLS | Pure RLS-based access control | Centralized, testable logic; RLS kept as backstop only |
| Supabase for Postgres + Auth | Self-managed Postgres + custom OAuth | Removes OAuth implementation burden, managed backups |
| Upstash Redis for caching + rate limiting | No cache layer; self-hosted Redis | Serverless, zero ops, sufficient for small scale |
| One reaction per viewer per entry (upsert, not append) | Allow multiple stacked reactions per viewer | Matches confirmed requirement; simpler data model and UI |
| Share links keyed by random token, not entry ID in URL | Expose entry UUID directly | Prevents enumeration/guessing of entries |
| Revoked/unknown share link both return generic 404 | Distinguish "revoked" vs "never existed" | Avoids leaking information about link history |
