import React from 'react';
import styles from './StartWritingChip.module.css';

export default function StartWritingChip({ onClick }) {
  return (
    <button type="button" className={styles.chip} onClick={onClick} aria-label="Start writing">
      <span className={styles.plus} aria-hidden="true">
        +
      </span>
      <span className={`label-sm ${styles.label}`}>start writing</span>
    </button>
  );
}
