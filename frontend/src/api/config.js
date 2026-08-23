const PROD_API_URL = 'https://lekha-likhi-api.onrender.com';

function firstNonemptyUrl(...candidates) {
  for (const raw of candidates) {
    const value = typeof raw === 'string' ? raw.trim().replace(/\/$/, '') : '';
    if (value) return value;
  }
  return '';
}

export function isLocalHostname(hostname) {
  return hostname === 'localhost' || hostname === '127.0.0.1';
}

export function isLocalApiUrl(url) {
  try {
    return isLocalHostname(new URL(url).hostname);
  } catch {
    return false;
  }
}

function pageHostname() {
  if (typeof window === 'undefined') return '';
  return window.location.hostname;
}

export function resolveApiUrl(env = {}, hostname = '') {
  const wantLocal = (env.VITE_APP_ENV || '').trim().toLowerCase() === 'local';
  const prod = firstNonemptyUrl(env.VITE_API_URL_PROD, PROD_API_URL);
  const resolved = firstNonemptyUrl(
    env.VITE_API_URL_TUNNEL,
    wantLocal ? env.VITE_API_URL_LOCAL : '',
    env.VITE_API_URL_PROD,
    wantLocal ? env.VITE_API_URL : '',
    PROD_API_URL,
  );

  // Public pages must never call loopback, even if a dashboard env still says localhost.
  if (hostname && !isLocalHostname(hostname) && isLocalApiUrl(resolved)) {
    return isLocalApiUrl(prod) ? PROD_API_URL : prod;
  }

  return resolved;
}

export function getApiUrl() {
  return resolveApiUrl(import.meta.env, pageHostname());
}

export function backendUnreachableMessage(apiUrl = getApiUrl()) {
  if (isLocalApiUrl(apiUrl)) {
    return 'Cannot reach the backend. Start it with: cd backend && uvicorn app.main:app --port 8000';
  }
  return 'The journal server is waking up. Wait a moment and try again.';
}

export async function checkApiHealth() {
  const apiUrl = getApiUrl();
  const controller = new AbortController();
  const timeoutMs = isLocalApiUrl(apiUrl) ? 4000 : 45000;
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${apiUrl}/health`, {
      signal: controller.signal,
    });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
}
