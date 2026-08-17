import React from 'react';
import StartWritingChip from './StartWritingChip';
import PageStack from './PageStack';
import styles from './PageFan.module.css';

export default function PageFan({
  entries,
  activeIndex,
  hasToday,
  onIndexChange,
  onEntryChange,
  onNewEntry,
  autoFocusId,
  shareControls,
  initialCaret,
  initialScrollTop,
  onCaretChange,
  onScrollChange,
}) {
  return (
    <div className={styles.fan}>
      {!hasToday ? (
        <div className={styles.leading}>
          <StartWritingChip onClick={onNewEntry} />
        </div>
      ) : null}

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
