import { apiFetch } from './client';

export async function getSharedEntry(token) {
  return apiFetch(`/shared/${token}`);
}
