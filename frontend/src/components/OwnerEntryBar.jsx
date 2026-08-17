import React from 'react';
import ReactionBar from './ReactionBar';
import styles from './OwnerEntryBar.module.css';

export default function OwnerEntryBar({
  shareToken,
  copied,
  onShare,
  shareDisabled,
  emojis,
  groups,
  selected,
  onSelect,
}) {
  const reactionsDisabled = !shareToken;

  return (
    <div className={styles.anchor}>
      <div className={styles.scrap}>
        <div className={styles.strip}>
          <button
            type="button"
            className={`${styles.shareStamp}${copied ? ` ${styles.copied}` : ''}`}
            onClick={onShare}
            disabled={shareDisabled}
            aria-label={shareToken ? 'Copy share link' : 'Create share link'}
          >
            <span className={`label-sm ${styles.shareLabel}`}>
              {copied ? 'copied!' : shareToken ? 'copy link' : 'share link'}
            </span>
            {copied ? (
              <span className={styles.inkDot} aria-hidden="true" />
            ) : null}
          </button>
          <ReactionBar
            emojis={emojis}
            groups={groups}
            selected={selected}
            onSelect={onSelect}
            disabled={reactionsDisabled}
            embedded
          />
        </div>
      </div>
    </div>
  );
}
