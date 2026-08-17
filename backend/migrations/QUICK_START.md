# 🚀 Quick Start: Apply RLS Migration

## ⚡ Fast Track (5 minutes)

### 1. Open Supabase SQL Editor
```
🌐 https://app.supabase.com → Your Project → SQL Editor
```

### 2. Run the Migration
- Click **"+ New query"**
- Copy entire contents of `002_rls_policies.sql`
- Paste and click **"Run"** (or Ctrl+Enter)
- ✅ All statements should execute successfully

### 3. Verify (Quick Check)
Paste this into SQL Editor:
```sql
SELECT tablename, COUNT(*) as policies
FROM pg_policies
WHERE tablename IN ('users', 'entries', 'share_links', 'reactions')
GROUP BY tablename;
```

**Expected Result:**
```
users         | 3
entries       | 4
share_links   | 4
reactions     | 4
```

### 4. Done! ✅
Your RLS policies are active. FastAPI will continue working normally.

---

## 📚 Need More Details?

- **Full Instructions:** See `README.md`
- **Verification:** See `VERIFICATION_CHECKLIST.md`
- **Task Summary:** See `TASK_7_COMPLETION_SUMMARY.md`

---

## 🆘 Troubleshooting

### "policy already exists"
✅ Safe to ignore - migration was already applied

### "permission denied"
❌ Check you're connected to the right database with admin privileges

### Want to rollback?
See the rollback script in `README.md`

---

## 📋 What This Migration Does

✅ Enables Row-Level Security on 4 tables (users, entries, share_links, reactions)
✅ Creates 15 security policies as defense-in-depth backstop
✅ Users can only access their own entries
✅ Users can only react with their own user_id
✅ No impact on FastAPI performance (service role bypasses RLS)

---

**Questions?** Check the detailed documentation in `README.md`
