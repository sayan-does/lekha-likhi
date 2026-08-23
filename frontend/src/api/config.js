const PROD_API_URL = 'https://lekha-likhi-api.onrender.com';

function firstNonemptyUrl(...candidates) {
  for (const raw of candidates) {
    const value = typeof raw === 'string' ? raw.trim().replace(/\/$/, '') : '';
    if (value) return value;
  }
  return '';
}

export function getApiUrl() {
  const env = import.meta.env;
  return firstNonemptyUrl(
    env.VITE_API_URL_TUNNEL,
    (env.VITE_APP_ENV || '').trim().toLowerCase() === 'local'
      ? env.VITE_API_URL_LOCAL
      : '',
    env.VITE_API_URL_PROD,
    env.VITE_API_URL,
    PROD_API_URL,
  );
}

export async function checkApiHealth() {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 4000);
  try {
    const response = await fetch(`${getApiUrl()}/health`, {
      signal: controller.signal,
    });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
}
