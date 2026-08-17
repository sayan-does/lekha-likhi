import React, { useState, useRef } from 'react';
import JournalPage from './JournalPage';
import styles from './PageStack.module.css';

export default function PageStack({ entries, activeIndex, onIndexChange }) {
  const containerRef = useRef(null);
  
  // Basic touch tracking for future swipe implementation
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);

  // Minimum swipe distance (in px)
  const minSwipeDistance = 50;

  const onTouchStart = (e) => {
    setTouchEnd(null); // Reset
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e) => setTouchEnd(e.targetTouches[0].clientX);

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe && activeIndex < entries.length - 1) {
      onIndexChange(activeIndex + 1); // Turn to next page (older entry)
    }
    if (isRightSwipe && activeIndex > 0) {
      onIndexChange(activeIndex - 1); // Turn to previous page (newer entry)
    }
  };

  return (
    <div 
      className={styles.perspectiveContainer}
      ref={containerRef}
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      {entries.map((entry, index) => {
        // Windowed rendering: only render active and adjacent pages
        if (Math.abs(index - activeIndex) > 1) return null;

        let pageState = 'active';
        if (index < activeIndex) pageState = 'past'; // Turned over (left)
        if (index > activeIndex) pageState = 'future'; // Underneath (right)

        return (
          <div 
            key={entry.id || index}
            className={`${styles.pageWrapper} ${styles[pageState]}`}
            style={{ zIndex: entries.length - index }}
          >
            <JournalPage 
              initialEntry={entry.content} 
              dateLabel={entry.date}
              isEditMode={index === 0} // Only latest page is editable for now
              pageSeed={entry.id || index}
            />
          </div>
        );
      })}
    </div>
  );
}
