import React, { useState } from 'react';
import styles from './ReactionBar.module.css';

export default function ReactionBar() {
  const allowedEmojis = ['❤️', '🔥', '🤔', '😂', '😢'];
  const [activeReaction, setActiveReaction] = useState(null);

  // Mock reactors
  const mockReactors = {
    '❤️': ['Sayan', 'Priya'],
    '😂': ['Aman']
  };

  return (
    <div className={styles.reactionBarContainer}>
      <div className={styles.reactionBar}>
        <div className={styles.emojiRow}>
          {allowedEmojis.map(emoji => (
            <button 
              key={emoji}
              className={`${styles.reactionButton} ${activeReaction === emoji ? styles.active : ''}`}
              onClick={() => setActiveReaction(emoji === activeReaction ? null : emoji)}
            >
              <span className={styles.emoji}>{emoji}</span>
            </button>
          ))}
        </div>
        
        <div className={styles.reactorNames}>
          {allowedEmojis.map(emoji => {
            let names = mockReactors[emoji] || [];
            if (activeReaction === emoji && !names.includes('You')) {
              names = [...names, 'You'];
            }
            if (names.length === 0) return null;
            return (
              <span key={emoji} className={`label-sm ${styles.nameGroup}`}>
                {emoji} {names.join(', ')}
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
}
