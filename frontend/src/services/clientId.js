const STORAGE_KEY = "track_client_id_v1";

function generateId() {
  if (window.crypto?.randomUUID) {
    return window.crypto.randomUUID();
  }
  return `client-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function resolveClientId() {
  try {
    const existing = sessionStorage.getItem(STORAGE_KEY);
    if (existing) {
      return existing;
    }
    const generated = generateId();
    sessionStorage.setItem(STORAGE_KEY, generated);
    return generated;
  } catch {
    return generateId();
  }
}

export const clientId = resolveClientId();
