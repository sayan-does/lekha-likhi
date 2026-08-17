import React, { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getSharedEntry } from '../api/shared';
import { groupReactions, postReaction } from '../api/reactions';
import JournalPage from './JournalPage';
import ReactionBar from './ReactionBar';
import CoverShell from './CoverShell';
import styles from './SharedPage.module.css';

const DATE_FORMAT = { month: 'long', day: 'numeric' };
const PREVIEW_TOKEN = 'preview';

function formatEntryDate(isoDate) {
  const [year, month, day] = isoDate.split('-').map(Number);
  return new Intl.DateTimeFormat(undefined, DATE_FORMAT).format(
    new Date(year, month - 1, day),
  );
}

function formatToday() {
  return new Intl.DateTimeFormat(undefined, DATE_FORMAT).format(new Date());
}

function StatusShell({ message, className = styles.revoked }) {
  return (
    <CoverShell className={className} contentClassName={styles.revokedContent}>
      <p className={`body-md ${styles.revokedMessage}`}>{message}</p>
    </CoverShell>
  );
}

export default function SharedPage() {
  const { token } = useParams();
  const { user, isAuthenticated, isReady, login } = useAuth();
  const [entry, setEntry] = useState(null);
  const [reactionGroups, setReactionGroups] = useState([]);
  const [selectedEmoji, setSelectedEmoji] = useState(null);
  const [status, setStatus] = useState('loading');
  const isPreview = import.meta.env.DEV && token === PREVIEW_TOKEN;

  const applyEntry = useCallback(
    (data) => {
      setEntry(data);
      setReactionGroups(groupReactions(data.reactions ?? []));
      if (user?.display_name) {
        const mine = data.reactions?.find(
          (reaction) => reaction.display_name === user.display_name,
        );
        setSelectedEmoji(mine?.emoji ?? null);
      } else {
        setSelectedEmoji(null);
      }
    },
    [user],
  );

  const loadEntry = useCallback(async () => {
    if (!token || isPreview) return;

    setStatus('loading');
    try {
      const data = await getSharedEntry(token);
      applyEntry(data);
      setStatus('ok');
    } catch (error) {
      setEntry(null);
      setReactionGroups([]);
      setSelectedEmoji(null);
      setStatus(error.status === 404 ? 'revoked' : 'error');
    }
  }, [token, isPreview, applyEntry]);

  useEffect(() => {
    if (isPreview || !isReady) return;
    loadEntry();
  }, [isPreview, isReady, loadEntry]);

  async function handleReactionSelect(emoji) {
    if (!isAuthenticated) {
      login();
      return;
    }

    try {
      await postReaction(token, emoji);
      const data = await getSharedEntry(token);
      applyEntry(data);
    } catch {
      /* ignore */
    }
  }

  if (isPreview) {
    return (
      <CoverShell>
        <div className={`page-frame ${styles.pageFrame}`}>
          <JournalPage
            dateLabel={formatToday()}
            body=""
            isEditMode={false}
            pageSeed={token}
          />
        </div>
        <ReactionBar groups={[]} selected={selectedEmoji} onSelect={handleReactionSelect} />
      </CoverShell>
    );
  }

  if (!isReady || status === 'loading') {
    return null;
  }

  if (status === 'revoked') {
    return <StatusShell message="this page is no longer shared" />;
  }

  if (status === 'error') {
    return <StatusShell message="could not load this shared page" />;
  }

  return (
    <CoverShell>
      <div className={`page-frame ${styles.pageFrame}`}>
        <JournalPage
          dateLabel={formatEntryDate(entry.entry_date)}
          body={entry.body}
          isEditMode={false}
          pageSeed={token}
        />
      </div>
      <ReactionBar
        groups={reactionGroups}
        selected={selectedEmoji}
        onSelect={handleReactionSelect}
      />
    </CoverShell>
  );
}
