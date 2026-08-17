export function todayIso(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function firstLinePreview(content) {
  if (!content) return '';
  const line = content.split('\n').find((l) => l.trim()) ?? '';
  return line.trim();
}

export function pastEntriesOnly(entries, today) {
  return entries.filter((entry) => entry.date !== today);
}

export function formatLastWritten(entryDate, today) {
  if (!entryDate) return 'never';

  if (entryDate === today) return 'today';

  const todayDate = new Date(`${today}T12:00:00`);
  const entry = new Date(`${entryDate}T12:00:00`);
  const diffDays = Math.round((todayDate - entry) / (1000 * 60 * 60 * 24));

  if (diffDays === 1) return 'yesterday';

  return new Intl.DateTimeFormat(undefined, {
    month: 'long',
    day: 'numeric',
  }).format(entry);
}
