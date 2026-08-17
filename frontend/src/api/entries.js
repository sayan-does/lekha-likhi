import { apiFetch } from './client';

export function mapEntryFromApi(apiEntry) {
  return {
    id: apiEntry.id,
    date: apiEntry.entry_date,
    content: apiEntry.body,
  };
}

export async function listEntries(limit = 50) {
  const data = await apiFetch(`/entries?limit=${limit}`);
  return data.entries.map(mapEntryFromApi);
}

export async function upsertEntry(entryDate, body, options = {}) {
  const data = await apiFetch(`/entries/${entryDate}`, {
    method: 'PUT',
    body: JSON.stringify({ body }),
    ...options,
  });
  return mapEntryFromApi(data);
}

export async function deleteEntry(entryDate) {
  return apiFetch(`/entries/${entryDate}`, { method: 'DELETE' });
}
