import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { listEntries, upsertEntry } from '../api/entries';
import {
  buildShareTokenMap,
  createShareLink,
  listShareLinks,
} from '../api/shareLinks';
import { getReactions, groupReactions, postReaction } from '../api/reactions';
import JournalPage from './JournalPage';
import PageFan from './PageFan';
import StartWritingChip from './StartWritingChip';
import CoverShell from './CoverShell';
import { findIndexById } from './PageStack';
import { todayIso } from '../utils/entries';
import {
  applyDraftsToEntries,
  clearDraft,
  draftBody,
  loadWritingSession,
  saveWritingSession,
  setDraft,
} from '../utils/writingSession';
import styles from './Dashboard.module.css';

const DATE_FORMAT = { month: 'long', day: 'numeric' };
const SAVE_DEBOUNCE_MS = 800;

function resolveActiveIndex(entryList, today, searchParams, lastDate) {
  const targetId = searchParams.get('entryId');
  const targetDate = searchParams.get('date');
  const focusToday = searchParams.get('today') === '1';

  if (targetId) {
    const byId = findIndexById(entryList, targetId);
    if (byId >= 0) return byId;
  }

  if (targetDate) {
    const byDate = entryList.findIndex((entry) => entry.date === targetDate);
    if (byDate >= 0) return byDate;
  }

  if (focusToday) {
    const todayIdx = entryList.findIndex((entry) => entry.date === today);
    return todayIdx >= 0 ? todayIdx : 0;
  }

  if (lastDate) {
    const byLast = entryList.findIndex((entry) => entry.date === lastDate);
    if (byLast >= 0) return byLast;
  }

  const todayIdx = entryList.findIndex((entry) => entry.date === today);
  return todayIdx >= 0 ? todayIdx : 0;
}

function formatToday() {
  return new Intl.DateTimeFormat(undefined, DATE_FORMAT).format(new Date());
}

function totalReactionCount(groups) {
  return groups.reduce((sum, group) => sum + (group.names?.length ?? 0), 0);
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { accessToken, user } = useAuth();
  const sessionRef = useRef(loadWritingSession());
  const [entries, setEntries] = useState([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [autoFocusId, setAutoFocusId] = useState(null);
  const [shareTokensByEntryId, setShareTokensByEntryId] = useState({});
  const [reactionGroups, setReactionGroups] = useState([]);
  const [selectedEmoji, setSelectedEmoji] = useState(null);
  const [shareOpen, setShareOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);
  const [emptyDraft, setEmptyDraft] = useState(() =>
    draftBody(sessionRef.current.drafts, todayIso()),
  );
  const [initialCaret] = useState(() => sessionRef.current.caret);
  const [initialScrollTop] = useState(() => sessionRef.current.scrollTop);
  const saveTimerRef = useRef(null);
  const copiedTimerRef = useRef(null);
  const pendingSaveRef = useRef(null);
  const inFlightRef = useRef(null);
  const scrollRafRef = useRef(0);
  const entriesRef = useRef(entries);
  const activeIndexRef = useRef(activeIndex);

  const today = todayIso();
  const hasToday = entries.some((entry) => entry.date === today);
  const activeEntry = entries[activeIndex] ?? null;
  const activeShareToken = activeEntry
    ? shareTokensByEntryId[activeEntry.id] ?? null
    : null;
  const activeCaret =
    initialCaret &&
    (initialCaret.date == null || initialCaret.date === (activeEntry?.date ?? today))
      ? initialCaret
      : null;

  entriesRef.current = entries;
  activeIndexRef.current = activeIndex;

  const loadReactions = useCallback(
    async (token) => {
      const reactions = await getReactions(token);
      setReactionGroups(groupReactions(reactions));
      if (user?.display_name) {
        const mine = reactions.find((r) => r.display_name === user.display_name);
        setSelectedEmoji(mine?.emoji ?? null);
      } else {
        setSelectedEmoji(null);
      }
    },
    [user],
  );

  const flushSave = useCallback(async (keepalive = false) => {
    const pending = pendingSaveRef.current;
    if (!pending) return;
    if (inFlightRef.current === `${pending.date}:${pending.body}`) return;

    const snapshot = { ...pending };
    inFlightRef.current = `${snapshot.date}:${snapshot.body}`;
    clearTimeout(saveTimerRef.current);

    try {
      const saved = await upsertEntry(snapshot.date, snapshot.body, { keepalive });
      setEntries((prev) => {
        const next = [...prev];
        const existingIdx = next.findIndex((entry) => entry.date === saved.date);
        if (existingIdx >= 0) {
          next[existingIdx] = { ...saved, content: snapshot.body };
        } else {
          next.unshift(saved);
        }
        return next;
      });

      const stillPending = pendingSaveRef.current;
      if (stillPending?.date === snapshot.date && stillPending.body === snapshot.body) {
        pendingSaveRef.current = null;
        clearDraft(snapshot.date);
      }
    } catch {
      /* keep pending draft for the next attempt */
    } finally {
      if (inFlightRef.current === `${snapshot.date}:${snapshot.body}`) {
        inFlightRef.current = null;
      }
      const leftover = pendingSaveRef.current;
      if (leftover && (leftover.date !== snapshot.date || leftover.body !== snapshot.body)) {
        clearTimeout(saveTimerRef.current);
        saveTimerRef.current = setTimeout(() => {
          flushSave();
        }, SAVE_DEBOUNCE_MS);
      }
    }
  }, []);

  function scheduleSave(entryDate, body) {
    pendingSaveRef.current = { date: entryDate, body };
    setDraft(entryDate, body);
    clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      flushSave();
    }, SAVE_DEBOUNCE_MS);
  }

  useEffect(() => {
    if (!accessToken) return undefined;

    let cancelled = false;

    async function load() {
      setLoading(true);
      try {
        const [entryList, links] = await Promise.all([
          listEntries(50),
          listShareLinks(),
        ]);
        if (cancelled) return;

        const session = loadWritingSession();
        sessionRef.current = session;
        const merged = applyDraftsToEntries(entryList, session.drafts);
        setEntries(merged);
        setEmptyDraft(draftBody(session.drafts, today) || '');
        setShareTokensByEntryId(buildShareTokenMap(links));
        setActiveIndex(resolveActiveIndex(merged, today, searchParams, session.activeDate));
      } catch {
        if (!cancelled) setEntries([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [accessToken, today, searchParams]);

  useEffect(() => {
    setShareOpen(false);
  }, [activeIndex]);

  useEffect(() => {
    const entry = entries[activeIndex];
    const date = entry?.date ?? (emptyDraft ? today : null);
    if (!date) return;
    saveWritingSession({ activeDate: date });
  }, [activeIndex, entries, emptyDraft, today]);

  useEffect(() => {
    if (!activeShareToken) {
      setReactionGroups([]);
      setSelectedEmoji(null);
      return undefined;
    }

    let cancelled = false;

    loadReactions(activeShareToken).catch(() => {
      if (!cancelled) {
        setReactionGroups([]);
        setSelectedEmoji(null);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [activeShareToken, loadReactions]);

  useEffect(() => {
    function persistView() {
      const entry = entriesRef.current[activeIndexRef.current];
      saveWritingSession({
        activeDate: entry?.date ?? today,
      });
    }

    function onHide() {
      persistView();
      flushSave(true);
    }

    function onVisibility() {
      if (document.visibilityState === 'hidden') onHide();
    }

    document.addEventListener('visibilitychange', onVisibility);
    window.addEventListener('pagehide', onHide);

    return () => {
      document.removeEventListener('visibilitychange', onVisibility);
      window.removeEventListener('pagehide', onHide);
      clearTimeout(saveTimerRef.current);
      clearTimeout(copiedTimerRef.current);
      cancelAnimationFrame(scrollRafRef.current);
      persistView();
      flushSave(true);
    };
  }, [flushSave, today]);

  async function handleNewEntry() {
    if (hasToday) return;
    try {
      const saved = await upsertEntry(today, emptyDraft);
      pendingSaveRef.current = null;
      clearDraft(today);
      setEntries((prev) => [saved, ...prev]);
      setActiveIndex(0);
      setAutoFocusId(saved.id);
      setEmptyDraft('');
    } catch {
      /* ignore */
    }
  }

  function handleIndexChange(index) {
    setAutoFocusId(null);
    setActiveIndex(index);
    const entry = entries[index];
    if (entry) saveWritingSession({ activeDate: entry.date, scrollTop: 0, caret: null });
  }

  function handleEntryChange(index, content) {
    const entry = entries[index];
    if (entry) scheduleSave(entry.date, content);
    setEntries((prev) =>
      prev.map((item, itemIndex) =>
        itemIndex === index ? { ...item, content } : item,
      ),
    );
  }

  function handleEmptyDraftChange(content) {
    setEmptyDraft(content);
    scheduleSave(today, content);
  }

  function handleCaretChange(caret) {
    const date = activeEntry?.date ?? today;
    saveWritingSession({ caret: { ...caret, date } });
  }

  function handleScrollChange(scrollTop) {
    if (scrollRafRef.current) return;
    scrollRafRef.current = requestAnimationFrame(() => {
      scrollRafRef.current = 0;
      saveWritingSession({ scrollTop });
    });
  }

  function toggleShareOpen() {
    setShareOpen((open) => !open);
  }

  async function handleShare() {
    if (!activeEntry?.id) return;

    let token = shareTokensByEntryId[activeEntry.id];
    if (!token) {
      const response = await createShareLink(activeEntry.id);
      token = response.token;
      setShareTokensByEntryId((prev) => ({ ...prev, [activeEntry.id]: token }));
      try {
        await loadReactions(token);
      } catch {
        /* reactions may be empty */
      }
    }

    const url = `${window.location.origin}/shared/${token}`;
    await navigator.clipboard.writeText(url);
    setCopied(true);
    clearTimeout(copiedTimerRef.current);
    copiedTimerRef.current = setTimeout(() => setCopied(false), 2000);
  }

  async function handleReactionSelect(emoji) {
    if (!activeShareToken) return;
    try {
      await postReaction(activeShareToken, emoji);
      await loadReactions(activeShareToken);
    } catch {
      /* ignore */
    }
  }

  const shareControls = activeEntry?.id
    ? {
        isOpen: shareOpen,
        onToggle: toggleShareOpen,
        onClose: () => setShareOpen(false),
        hasLink: Boolean(activeShareToken),
        reactionCount: totalReactionCount(reactionGroups),
        shareToken: activeShareToken,
        copied,
        onShare: handleShare,
        groups: reactionGroups,
        selected: selectedEmoji,
        onReactionSelect: handleReactionSelect,
      }
    : undefined;

  return (
    <CoverShell className={styles.root}>
      <button
        type="button"
        className={`label-sm ${styles.close}`}
        onClick={() => navigate('/')}
        aria-label="Close notebook"
      >
        close
      </button>
      <div className={styles.layout}>
        {loading ? (
          <p className={`body-md ${styles.loading}`}>opening notebook…</p>
        ) : entries.length === 0 ? (
          <div className={styles.emptyFan}>
            <div className={styles.leading}>
              <StartWritingChip onClick={handleNewEntry} />
            </div>
            <div className={styles.center}>
              <JournalPage
                dateLabel={formatToday()}
                body={emptyDraft}
                isEditMode
                autoFocus={false}
                pageSeed="empty"
                emptyPrompt="nothing written yet — tap to begin"
                onChange={handleEmptyDraftChange}
                initialCaret={activeCaret}
                initialScrollTop={initialScrollTop}
                onCaretChange={handleCaretChange}
                onScrollChange={handleScrollChange}
              />
            </div>
          </div>
        ) : (
          <PageFan
            entries={entries}
            activeIndex={activeIndex}
            hasToday={hasToday}
            onIndexChange={handleIndexChange}
            onEntryChange={handleEntryChange}
            onNewEntry={handleNewEntry}
            autoFocusId={autoFocusId}
            shareControls={shareControls}
            initialCaret={activeCaret}
            initialScrollTop={initialScrollTop}
            onCaretChange={handleCaretChange}
            onScrollChange={handleScrollChange}
          />
        )}
      </div>
    </CoverShell>
  );
}
