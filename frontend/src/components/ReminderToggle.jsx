import React, { useEffect, useState } from 'react';
import { getPushStatus, subscribePush, unsubscribePush } from '../api/push';
import {
  disablePushReminders,
  enablePushReminders,
  getBrowserTimezone,
  isPushSupported,
  subscriptionPayload,
} from '../utils/pushNotifications';
import styles from './ReminderToggle.module.css';

export default function ReminderToggle() {
  const [enabled, setEnabled] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const supported = isPushSupported();

  useEffect(() => {
    if (!supported) {
      setLoading(false);
      return;
    }

    let cancelled = false;
    getPushStatus()
      .then((status) => {
        if (!cancelled) setEnabled(Boolean(status.enabled && status.subscribed));
      })
      .catch(() => {
        if (!cancelled) setEnabled(false);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [supported]);

  async function handleToggle() {
    if (busy || loading) return;
    setBusy(true);
    setError('');

    try {
      const timezone = getBrowserTimezone();
      if (enabled) {
        const subscription = await disablePushReminders();
        if (subscription) {
          await unsubscribePush(subscriptionPayload(subscription), timezone);
        }
        setEnabled(false);
      } else {
        const subscription = await enablePushReminders();
        await subscribePush(subscriptionPayload(subscription), timezone);
        setEnabled(true);
      }
    } catch (err) {
      setError(err.message || 'Could not update reminders.');
      setEnabled(false);
    } finally {
      setBusy(false);
    }
  }

  if (!supported) return null;

  return (
    <div className={styles.root}>
      <button
        type="button"
        className={`label-sm ${styles.toggle} ${enabled ? styles.toggleOn : ''}`}
        onClick={handleToggle}
        disabled={loading || busy}
        aria-pressed={enabled}
      >
        {loading ? 'checking reminders…' : enabled ? 'reminders on' : 'remind me to write'}
      </button>
      <p className={`body-md ${styles.hint}`}>
        {enabled
          ? 'A gentle nudge every 4 hours until you write today.'
          : 'Get a nudge every 4 hours until you write today.'}
      </p>
      {error ? <p className={`body-md ${styles.error}`}>{error}</p> : null}
    </div>
  );
}
