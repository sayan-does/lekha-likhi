import { apiFetch } from './client';

export function groupReactions(reactions) {
  const groups = new Map();
  for (const reaction of reactions) {
    if (!groups.has(reaction.emoji)) {
      groups.set(reaction.emoji, []);
    }
    groups.get(reaction.emoji).push(reaction.display_name);
  }
  return Array.from(groups.entries()).map(([emoji, names]) => ({ emoji, names }));
}

export async function getReactions(token) {
  return apiFetch(`/shared/${token}/reactions`);
}

export async function postReaction(token, emoji) {
  return apiFetch(`/shared/${token}/react`, {
    method: 'POST',
    body: JSON.stringify({ emoji }),
  });
}
