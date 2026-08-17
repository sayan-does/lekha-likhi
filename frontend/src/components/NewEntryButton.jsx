import React from 'react';
import styles from './NewEntryButton.module.css';

export default function NewEntryButton({ onClick, isHidden }) {
  if (isHidden) return null;

  return (
    <button
      type="button"
      className={styles.fab}
      onClick={onClick}
      aria-label="New entry"
    >
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={styles.icon}
        aria-hidden="true"
      >
        <path d="M12 4s-1 8 0 16" />
        <path d="M4 12s8-1 16 0" />
      </svg>
    </button>
  );
}
