const STORAGE_KEY = 'writing_session';

function emptySession() {
  return {
    drafts: {},
    activeDate: null,
    caret: null,
    scrollTop: 0,
  };
}

export function loadWritingSession() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptySession();
    const parsed = JSON.parse(raw);
    return {
      drafts: parsed.drafts && typeof parsed.drafts === 'object' ? parsed.drafts : {},
      activeDate: typeof parsed.activeDate === 'string' ? parsed.activeDate : null,
      caret: parsed.caret && typeof parsed.caret === 'object' ? parsed.caret : null,
      scrollTop: Number.isFinite(parsed.scrollTop) ? parsed.scrollTop : 0,
    };
  } catch {
    return emptySession();
  }
}

export function saveWritingSession(patch) {
  const current = loadWritingSession();
  const next = {
    ...current,
    ...patch,
    drafts: patch.drafts ? { ...current.drafts, ...patch.drafts } : current.drafts,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next;
}

export function setDraft(date, body) {
  return saveWritingSession({
    drafts: { [date]: { body, updatedAt: Date.now() } },
    activeDate: date,
  });
}

export function clearDraft(date) {
  const current = loadWritingSession();
  if (!current.drafts[date]) return current;
  const drafts = { ...current.drafts };
  delete drafts[date];
  const next = { ...current, drafts };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next;
}

export function clearWritingSession() {
  localStorage.removeItem(STORAGE_KEY);
}

export function applyDraftsToEntries(entries, drafts) {
  if (!drafts) return entries;
  return entries.map((entry) => {
    const draft = drafts[entry.date];
    if (!draft || typeof draft.body !== 'string') return entry;
    return { ...entry, content: draft.body };
  });
}

export function draftBody(drafts, date) {
  const draft = drafts?.[date];
  return typeof draft?.body === 'string' ? draft.body : '';
}
