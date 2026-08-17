import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import JournalPage from './JournalPage';
import ReactionBar from './ReactionBar';
import styles from './SharedPage.module.css';

const DATE_FORMAT = { month: 'long', day: 'numeric' };
const PREVIEW_TOKEN = 'preview';

function formatToday() {
  return new Intl.DateTimeFormat(undefined, DATE_FORMAT).format(new Date());
}

export default function SharedPage() {
  const { token } = useParams();
  const [selected, setSelected] = useState(null);
  const isPreview = import.meta.env.DEV && token === PREVIEW_TOKEN;

  if (!isPreview) {
    return (
      <div className={`cover ${styles.revoked}`}>
        <p className={`body-md ${styles.revokedMessage}`}>
          this page is no longer shared
        </p>
      </div>
    );
  }

  return (
    <div className="cover">
      <div className={`page-frame ${styles.pageFrame}`}>
        <JournalPage
          dateLabel={formatToday()}
          body=""
          isEditMode={false}
          pageSeed={token}
        />
      </div>
      <ReactionBar
        groups={[]}
        selected={selected}
        onSelect={setSelected}
      />
    </div>
  );
}
