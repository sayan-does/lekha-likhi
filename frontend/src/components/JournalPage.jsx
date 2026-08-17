import React from 'react';
import PaperSurface from './PaperSurface';
import styles from './JournalPage.module.css';

export default function JournalPage({
  dateLabel,
  body = '',
  isEditMode = false,
  autoFocus = false,
  pageSeed,
  onChange,
  emptyPrompt,
}) {
  const text = body ?? '';
  const hasDate = Boolean(dateLabel);
  const isEmpty = text.length === 0;
  const showPrompt = !isEditMode && isEmpty && Boolean(emptyPrompt);

  return (
    <PaperSurface pageSeed={pageSeed}>
      <div className={styles.page}>
        {hasDate ? (
          <p className={`headline-md ${styles.date}`}>{dateLabel}</p>
        ) : null}

        {isEditMode ? (
          <textarea
            className={`body-lg ${styles.editor}`}
            value={text}
            onChange={(event) => onChange?.(event.target.value)}
            aria-label={dateLabel || 'Journal entry'}
            spellCheck={false}
            autoFocus={autoFocus}
          />
        ) : (
          <div className={`body-lg ${styles.body}`}>
            {showPrompt ? (
              <span className={styles.prompt}>{emptyPrompt}</span>
            ) : (
              text
            )}
          </div>
        )}
      </div>
    </PaperSurface>
  );
}
