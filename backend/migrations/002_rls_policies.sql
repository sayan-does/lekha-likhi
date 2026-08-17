-- Migration 002: Row-Level Security Policies (Defense-in-Depth Backstop)
-- 
-- Purpose: Enable RLS on all tables and add policies as a security backstop.
-- Note: FastAPI is the primary authorization layer. These policies serve as
--       defense-in-depth protection in case the service role key is misused
--       or a bug bypasses application-layer checks.

-- ============================================================================
-- 1. ENABLE ROW-LEVEL SECURITY ON ALL TABLES
-- ============================================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE share_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE reactions ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 2. USERS TABLE POLICIES
-- ============================================================================

-- Users can read their own user record
CREATE POLICY "Users can view their own profile"
  ON users
  FOR SELECT
  USING (auth.uid() = id);

-- Users can update their own user record (for profile updates)
CREATE POLICY "Users can update their own profile"
  ON users
  FOR UPDATE
  USING (auth.uid() = id);

-- Allow the application to insert new user records (via service role)
-- Note: This policy allows authenticated users to insert their own record
CREATE POLICY "Users can insert their own profile"
  ON users
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- ============================================================================
-- 3. ENTRIES TABLE POLICIES
-- ============================================================================

-- Users can only view their own entries
CREATE POLICY "Users can view their own entries"
  ON entries
  FOR SELECT
  USING (auth.uid() = owner_id);

-- Users can only insert entries where they are the owner
CREATE POLICY "Users can create their own entries"
  ON entries
  FOR INSERT
  WITH CHECK (auth.uid() = owner_id);

-- Users can only update their own entries
CREATE POLICY "Users can update their own entries"
  ON entries
  FOR UPDATE
  USING (auth.uid() = owner_id);

-- Users can only delete their own entries
CREATE POLICY "Users can delete their own entries"
  ON entries
  FOR DELETE
  USING (auth.uid() = owner_id);

-- ============================================================================
-- 4. SHARE_LINKS TABLE POLICIES
-- ============================================================================

-- Users can view share links for their own entries
CREATE POLICY "Users can view share links for their entries"
  ON share_links
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM entries
      WHERE entries.id = share_links.entry_id
      AND entries.owner_id = auth.uid()
    )
  );

-- Users can create share links for their own entries
CREATE POLICY "Users can create share links for their entries"
  ON share_links
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM entries
      WHERE entries.id = share_links.entry_id
      AND entries.owner_id = auth.uid()
    )
  );

-- Users can update (revoke) share links for their own entries
CREATE POLICY "Users can update share links for their entries"
  ON share_links
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM entries
      WHERE entries.id = share_links.entry_id
      AND entries.owner_id = auth.uid()
    )
  );

-- Users can delete share links for their own entries
CREATE POLICY "Users can delete share links for their entries"
  ON share_links
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM entries
      WHERE entries.id = share_links.entry_id
      AND entries.owner_id = auth.uid()
    )
  );

-- ============================================================================
-- 5. REACTIONS TABLE POLICIES
-- ============================================================================

-- Anyone can view reactions (needed for shared entry viewing)
-- This is safe because reactions are only viewable in the context of
-- a valid share link, which is enforced at the application layer
CREATE POLICY "Anyone can view reactions"
  ON reactions
  FOR SELECT
  USING (true);

-- Users can only insert reactions with their own user_id
-- This prevents impersonation of other users when reacting
CREATE POLICY "Users can only react as themselves"
  ON reactions
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can only update their own reactions
CREATE POLICY "Users can update their own reactions"
  ON reactions
  FOR UPDATE
  USING (auth.uid() = user_id);

-- Users can only delete their own reactions
CREATE POLICY "Users can delete their own reactions"
  ON reactions
  FOR DELETE
  USING (auth.uid() = user_id);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
