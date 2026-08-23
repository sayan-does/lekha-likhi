import React from 'react';
import PageStack from './PageStack';
import styles from './PageFan.module.css';

export default function PageFan({
  entries,
  activeIndex,
  onIndexChange,
  onEntryChange,
  autoFocusId,
  shareControls,
  initialCaret,
  initialScrollTop,
  onCaretChange,
  onScrollChange,
}) {
  return (
    <div className={styles.fan}>
      <div className={styles.center}>
        <PageStack
          entries={entries}
          activeIndex={activeIndex}
          onIndexChange={onIndexChange}
          onEntryChange={onEntryChange}
          autoFocusId={autoFocusId}
          shareControls={shareControls}
          initialCaret={initialCaret}
          initialScrollTop={initialScrollTop}
          onCaretChange={onCaretChange}
          onScrollChange={onScrollChange}
        />
      </div>
    </div>
  );
}
