import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { deleteEntry, listEntries } from '../api/entries';
import PastEntryRow from './PastEntryRow';
import CoverShell from './CoverShell';
import { pastEntriesOnly, todayIso } from '../utils/entries';
import styles from './ArchivePage.module.css';

export default function ArchivePage() {
  const navigate = useNavigate();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const [confirmEntry, setConfirmEntry] = useState(null);
  const today = todayIso();

  async function loadEntries() {
    setLoading(true);
    try {
      const data = await listEntries(50);
      setEntries(pastEntriesOnly(data, today));
    } catch {
      setEntries([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadEntries();
  }, [today]);

  async function handleDelete(entry) {
    setConfirmEntry(null);
    setDeletingId(entry.id);
    try {
      await deleteEntry(entry.date);
      setEntries((prev) => prev.filter((e) => e.id !== entry.id));
    } catch {
      /* ignore */
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <CoverShell className={styles.root}>
      <div className={styles.scroll}>
        <header className={styles.header}>
          <button
            type="button"
            className={`label-sm ${styles.back}`}
            onClick={() => navigate('/')}
          >
            ← back
          </button>
          <h1 className={`headline-md ${styles.title}`}>past writings</h1>
        </header>

        {loading ? (
          <p className={`body-md ${styles.loading}`}>loading entries…</p>
        ) : entries.length === 0 ? (
          <p className={`body-md ${styles.empty}`}>no past pages yet</p>
        ) : (
          <ul className={styles.list}>
            {entries.map((entry) => (
              <li key={entry.id}>
                <PastEntryRow
                  entry={entry}
                  onDelete={(target) => setConfirmEntry(target)}
                  isDeleting={deletingId === entry.id}
                />
              </li>
            ))}
          </ul>
        )}

        {confirmEntry ? (
          <div className={styles.confirmBackdrop}>
            <div className={styles.confirmScrap} role="dialog" aria-label="Confirm delete">
              <p className={`body-md ${styles.confirmText}`}>
                delete this page permanently?
              </p>
              <div className={styles.confirmActions}>
                <button
                  type="button"
                  className={styles.confirmCancel}
                  onClick={() => setConfirmEntry(null)}
                >
                  keep
                </button>
                <button
                  type="button"
                  className={styles.confirmDelete}
                  onClick={() => handleDelete(confirmEntry)}
                >
                  delete
                </button>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </CoverShell>
  );
}
