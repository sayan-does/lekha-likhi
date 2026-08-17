import React from 'react';
import { formatEntryDate } from './PageStack';
import styles from './PastPagesIndex.module.css';

function firstLinePreview(content) {
  if (!content) return '';
  const line = content.split('\n').find((l) => l.trim()) ?? '';
  return line.trim();
}

export default function PastPagesIndex({
  entries,
  todayIso,
  activeEntryId,
  onSelect,
}) {
  const pastEntries = entries.filter((entry) => entry.date !== todayIso);

  return (
    <div className={styles.slot}>
      <div className={styles.scrap}>
        {pastEntries.length === 0 ? (
          <p className={`body-md ${styles.empty}`}>no past pages yet</p>
        ) : (
          <ul className={styles.list}>
            {pastEntries.map((entry) => {
              const isActive = entry.id === activeEntryId;
              const preview = firstLinePreview(entry.content);
              return (
                <li key={entry.id}>
                  <button
                    type="button"
                    className={`${styles.row}${isActive ? ` ${styles.active}` : ''}`}
                    onClick={() => onSelect(entry.id)}
                  >
                    <span className={`label-sm ${styles.date}`}>
                      {formatEntryDate(entry.date)}
                    </span>
                    <span className={`body-md ${styles.preview}`}>
                      {preview || '—'}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
