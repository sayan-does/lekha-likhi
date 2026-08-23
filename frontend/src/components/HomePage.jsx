import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { listEntries } from '../api/entries';
import CoverShell from './CoverShell';
import Logo from './Logo';
import { formatEntryDate } from './PageStack';
import {
  formatLastWritten,
  firstLinePreview,
  pastEntriesOnly,
  todayIso,
} from '../utils/entries';
import ReminderToggle from './ReminderToggle';
import styles from './HomePage.module.css';

const PREVIEW_LIMIT = 3;

export default function HomePage() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const today = todayIso();

  useEffect(() => {
    let cancelled = false;

    listEntries(50)
      .then((data) => {
        if (!cancelled) setEntries(data);
      })
      .catch(() => {
        if (!cancelled) setEntries([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const pastEntries = pastEntriesOnly(entries, today);
  const previewEntries = [...pastEntries]
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, PREVIEW_LIMIT);
  const lastEntry = previewEntries[0] ?? null;

  return (
    <CoverShell className={styles.root} contentClassName={styles.shell}>
      <div className={styles.scroll}>
        <header className={styles.header}>
          <h1 className={styles.title}>
            <Logo className={styles.logo} />
          </h1>
          <p className={`body-md ${styles.tagline}`}>Open your notebook to begin writing.</p>
        </header>

        <button
          type="button"
          className={styles.startCard}
          onClick={() => navigate('/write?today=1')}
        >
          <span className={`headline-md ${styles.startPrompt}`}>what&apos;s on your mind?</span>
          <span className={`body-md ${styles.startHint}`}>tap to write today</span>
        </button>

        <ReminderToggle />

        {!loading ? (
          <div
            role="button"
            tabIndex={0}
            className={styles.pastNotesCard}
            onClick={() => navigate('/archive')}
            onKeyDown={(event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                navigate('/archive');
              }
            }}
          >
            <span className={`headline-md ${styles.pastNotesTitle}`}>notes from the past</span>
            <span className={`body-md ${styles.pastNotesHint}`}>
              {lastEntry ? (
                <>
                  last written:{' '}
                  <em>{formatLastWritten(lastEntry.date, today)}</em>
                </>
              ) : (
                'no past notes yet'
              )}
            </span>
            {previewEntries.length > 0 ? (
              <ul className={styles.previewNotes}>
                {previewEntries.map((entry, index) => (
                  <li
                    key={entry.id}
                    className={styles.previewNote}
                    style={{ '--peek-index': index }}
                  >
                    <span className={`label-sm ${styles.previewNoteDate}`}>
                      {formatEntryDate(entry.date)}
                    </span>
                    <span className={`body-md ${styles.previewNoteText}`}>
                      {firstLinePreview(entry.content) || '—'}
                    </span>
                  </li>
                ))}
              </ul>
            ) : null}
            <span className={`label-sm ${styles.pastNotesAction}`}>tap to open all notes</span>
          </div>
        ) : null}

        {loading ? (
          <p className={`body-md ${styles.loading}`}>opening notebook…</p>
        ) : null}

        <button
          type="button"
          className={`label-sm ${styles.signOut}`}
          onClick={logout}
        >
          sign out
        </button>
      </div>
    </CoverShell>
  );
}
