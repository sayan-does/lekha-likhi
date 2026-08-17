import { apiFetch } from './client';

export async function listShareLinks() {
  return apiFetch('/share-links');
}

export function buildShareTokenMap(links) {
  const map = {};
  for (const link of links) {
    if (link.is_active) {
      map[link.entry_id] = link.token;
    }
  }
  return map;
}

export async function createShareLink(entryId) {
  return apiFetch(`/entries/${entryId}/share`, { method: 'POST' });
}
