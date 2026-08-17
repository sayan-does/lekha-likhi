import React from 'react';
import styles from './ReactionBar.module.css';

const DEFAULT_EMOJIS = ['❤️', '😢', '👏', '😂', '😮'];

export default function ReactionBar({
  emojis = DEFAULT_EMOJIS,
  groups = [],
  selected = null,
  onSelect,
}) {
  const namedGroups = groups.filter((group) => group.names?.length > 0);

  return (
    <div className={styles.anchor}>
      <div className={styles.scrap}>
        <div className={styles.strip}>
          <div className={styles.emojiRow}>
            {emojis.map((emoji) => {
              const isSelected = selected === emoji;
              return (
                <button
                  key={emoji}
                  type="button"
                  className={`${styles.tap} ${isSelected ? styles.selected : ''}`}
                  aria-pressed={isSelected}
                  aria-label={emoji}
                  onClick={() => onSelect?.(emoji)}
                >
                  <span className={styles.emoji} aria-hidden="true">
                    {emoji}
                  </span>
                </button>
              );
            })}
          </div>
          {namedGroups.length > 0 ? (
            <p className={`label-sm ${styles.names}`}>
              {namedGroups.map((group, index) => (
                <span key={group.emoji} className={styles.nameGroup}>
                  {index > 0 ? ' ' : ''}
                  {group.emoji} {group.names.join(', ')}
                </span>
              ))}
            </p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
