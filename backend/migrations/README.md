# Database Migrations

This folder contains SQL migration files for the Lekha-Likhi journal app backend.

## Migration Files

- `002_rls_policies.sql` - Row-Level Security policies for defense-in-depth protection

## Applying Migrations to Supabase

### Option 1: Using Supabase Dashboard (Recommended for Manual Application)

1. **Open the Supabase SQL Editor:**
   - Go to your Supabase project dashboard at https://app.supabase.com
   - Navigate to: **SQL Editor** (in the left sidebar)

2. **Create a new query:**
   - Click **"+ New query"** button

3. **Copy and paste the migration file:**
   - Open `002_rls_policies.sql`
   - Copy the entire contents
   - Paste into the SQL Editor

4. **Execute the migration:**
   - Click **"Run"** button (or press Ctrl+Enter)
   - Verify the output shows successful execution
   - All statements should complete without errors

5. **Verify the policies were created:**
   - Go to **Authentication > Policies** in the Supabase dashboard
   - You should see the new RLS policies listed for each table:
     - `users` (3 policies)
     - `entries` (4 policies)
     - `share_links` (4 policies)
     - `reactions` (4 policies)

### Option 2: Using Supabase CLI

If you have the Supabase CLI installed and linked to your project:

```bash
# From the backend/migrations directory
supabase db execute --file 002_rls_policies.sql
```

### Option 3: Using psql (Direct Database Connection)

If you have direct database access:

```bash
# Get connection string from Supabase dashboard: Settings > Database > Connection string
psql "your-connection-string-here" -f 002_rls_policies.sql
```

## Verification Steps

After applying the migration, verify that RLS is working correctly:

### 1. Check that RLS is enabled on all tables:

```sql
SELECT 
  schemaname,
  tablename,
  rowsecurity
FROM pg_tables
WHERE tablename IN ('users', 'entries', 'share_links', 'reactions');
```

Expected result: `rowsecurity` column should be `true` for all four tables.

### 2. List all policies:

```sql
SELECT 
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE tablename IN ('users', 'entries', 'share_links', 'reactions')
ORDER BY tablename, policyname;
```

Expected result: You should see 15 policies total:
- 3 for `users`
- 4 for `entries`
- 4 for `share_links`
- 4 for `reactions`

### 3. Test a policy (example):

```sql
-- Set a test user context (replace with a real user UUID from your auth.users table)
SET request.jwt.claims.sub = 'your-test-user-uuid-here';

-- Try to query entries - should only return entries owned by that user
SELECT * FROM entries;
```

## Important Notes

### Defense-in-Depth Architecture

These RLS policies are a **security backstop**, not the primary authorization layer:

- **Primary authorization:** FastAPI application code (in `backend/app/`)
- **Backstop authorization:** These RLS policies

The FastAPI layer already enforces all access control rules. These policies protect against:
- Accidental service role key exposure
- Bugs in the application authorization logic
- Direct database access attempts

### Service Role vs. Authenticated Queries

- **Service Role:** Bypasses RLS completely (used by FastAPI for most operations)
- **Authenticated Role:** Subject to RLS policies (good for testing, not used in production FastAPI)

The FastAPI backend uses the Supabase service role key, which means these policies won't affect normal application operation - they only kick in if someone tries to use an authenticated user token directly against the database.

### Policy Coverage

The policies enforce:

✅ Users can only access their own entries (SELECT, INSERT, UPDATE, DELETE)
✅ Users can only manage share links for their own entries
✅ Users can only create reactions with their own user_id (prevents impersonation)
✅ Users can only modify/delete their own reactions
✅ Reactions are viewable by anyone (safe because share link validation happens in FastAPI)

## Rollback

If you need to rollback this migration:

```sql
-- Drop all policies
DROP POLICY IF EXISTS "Users can view their own profile" ON users;
DROP POLICY IF EXISTS "Users can update their own profile" ON users;
DROP POLICY IF EXISTS "Users can insert their own profile" ON users;

DROP POLICY IF EXISTS "Users can view their own entries" ON entries;
DROP POLICY IF EXISTS "Users can create their own entries" ON entries;
DROP POLICY IF EXISTS "Users can update their own entries" ON entries;
DROP POLICY IF EXISTS "Users can delete their own entries" ON entries;

DROP POLICY IF EXISTS "Users can view share links for their entries" ON share_links;
DROP POLICY IF EXISTS "Users can create share links for their entries" ON share_links;
DROP POLICY IF EXISTS "Users can update share links for their entries" ON share_links;
DROP POLICY IF EXISTS "Users can delete share links for their entries" ON share_links;

DROP POLICY IF EXISTS "Anyone can view reactions" ON reactions;
DROP POLICY IF EXISTS "Users can only react as themselves" ON reactions;
DROP POLICY IF EXISTS "Users can update their own reactions" ON reactions;
DROP POLICY IF EXISTS "Users can delete their own reactions" ON reactions;

-- Disable RLS
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE entries DISABLE ROW LEVEL SECURITY;
ALTER TABLE share_links DISABLE ROW LEVEL SECURITY;
ALTER TABLE reactions DISABLE ROW LEVEL SECURITY;
```

## Troubleshooting

### "permission denied for table X"

This likely means:
1. RLS is enabled but no policy allows the operation
2. You're testing with an authenticated user token (not service role)
3. Solution: Use service role key in FastAPI, or add/adjust policies

### "policy X already exists"

The migration has already been applied. Check `pg_policies` to verify.

### Performance Concerns

RLS policies can add overhead to queries. However:
- FastAPI uses the service role key, which bypasses RLS entirely
- No performance impact on production operations
- Only affects direct database access with authenticated tokens
