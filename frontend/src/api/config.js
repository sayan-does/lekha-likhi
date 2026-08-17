export function getApiUrl() {
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
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
