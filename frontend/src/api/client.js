import { getApiUrl } from './config';

const API_URL = getApiUrl();

let tokenGetter = () => sessionStorage.getItem('access_token');

export function setTokenGetter(getter) {
  tokenGetter = getter;
}

export async function apiFetch(path, options = {}) {
  const token = tokenGetter();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!response.ok) {
    const error = new Error(response.statusText);
    error.status = response.status;
    try {
      error.body = await response.json();
    } catch {
      /* empty */
    }
    throw error;
  }

  if (response.status === 204) return null;
  return response.json();
}
