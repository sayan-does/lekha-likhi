import React from 'react';
import { useNavigate } from 'react-router-dom';
import { formatEntryDate } from './PageStack';
import { firstLinePreview } from '../utils/entries';
import styles from './PastEntryRow.module.css';

export default function PastEntryRow({ entry, onSelect, onDelete, isDeleting }) {
  const preview = firstLinePreview(entry.content);
  const navigate = useNavigate();

  function handleSelect() {
    if (onSelect) {
      onSelect(entry);
      return;
    }
    navigate(`/write?entryId=${entry.id}`);
  }

  return (
    <div className={styles.row}>
      <button type="button" className={styles.main} onClick={handleSelect}>
        <span className={`label-sm ${styles.date}`}>{formatEntryDate(entry.date)}</span>
        <span className={`body-md ${styles.preview}`}>{preview || '—'}</span>
      </button>
      {onDelete ? (
        <button
          type="button"
          className={styles.delete}
          aria-label={`Delete entry from ${formatEntryDate(entry.date)}`}
          disabled={isDeleting}
          onClick={() => onDelete(entry)}
        >
          ×
        </button>
      ) : null}
    </div>
  );
}
