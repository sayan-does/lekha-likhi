import { apiFetch } from './client';

export function getVapidPublicKey() {
  return apiFetch('/push/vapid-public-key');
}

export function getPushStatus() {
  return apiFetch('/push/status');
}

export function subscribePush(subscription, timezone) {
  return apiFetch('/push/subscribe', {
    method: 'POST',
    body: JSON.stringify({
      endpoint: subscription.endpoint,
      keys: {
        p256dh: subscription.keys.p256dh,
        auth: subscription.keys.auth,
      },
      timezone,
    }),
  });
}

export function unsubscribePush(subscription, timezone) {
  return apiFetch('/push/subscribe', {
    method: 'DELETE',
    body: JSON.stringify({
      endpoint: subscription.endpoint,
      keys: {
        p256dh: subscription.keys.p256dh,
        auth: subscription.keys.auth,
      },
      timezone,
    }),
  });
}
