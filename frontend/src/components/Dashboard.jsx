import React, { useState } from 'react';
import JournalPage from './JournalPage';
import NewEntryButton from './NewEntryButton';
import PageStack from './PageStack';
import styles from './Dashboard.module.css';

const DATE_FORMAT = { month: 'long', day: 'numeric' };

function todayIso(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatToday() {
  return new Intl.DateTimeFormat(undefined, DATE_FORMAT).format(new Date());
}

export default function Dashboard() {
  const [entries, setEntries] = useState([]);
  const [activeIndex, setActiveIndex] = useState(0);

  const today = todayIso();
  const hasToday = entries.some((entry) => entry.date === today);
  const isEmpty = entries.length === 0;

  function handleNewEntry() {
    setEntries((prev) => {
      if (prev.some((entry) => entry.date === today)) return prev;
      return [{ id: crypto.randomUUID(), date: today, content: '' }, ...prev];
    });
    setActiveIndex(0);
  }

  function handleEntryChange(index, content) {
    setEntries((prev) =>
      prev.map((entry, i) => (i === index ? { ...entry, content } : entry)),
    );
  }

  return (
    <div className="cover">
      <div className={`page-frame ${styles.frame}`}>
        {isEmpty ? (
          <div className={styles.stage} onClick={handleNewEntry}>
            <JournalPage
              dateLabel={formatToday()}
              body=""
              isEditMode={false}
              pageSeed="empty"
              emptyPrompt="nothing written yet — tap to begin"
            />
          </div>
        ) : (
          <div className={styles.stage}>
            <PageStack
              entries={entries}
              activeIndex={activeIndex}
              onIndexChange={setActiveIndex}
              onEntryChange={handleEntryChange}
            />
          </div>
        )}
        <NewEntryButton onClick={handleNewEntry} isHidden={hasToday} />
      </div>
    </div>
  );
}
