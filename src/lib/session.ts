/**
 * QalaJob AI — Session Management
 * Handles JWT tokens, role, and auth cookies.
 * Supports "Remember Me" (localStorage vs sessionStorage).
 */

const ACCESS_KEY = "qalajob-access";
const REFRESH_KEY = "qalajob-refresh";
const ROLE_KEY = "qalajob-role";
const REMEMBER_KEY = "qalajob-remember";

function getStorage(): Storage {
  if (typeof window === "undefined") return localStorage;
  const remember = localStorage.getItem(REMEMBER_KEY);
  return remember === "0" ? sessionStorage : localStorage;
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return getStorage().getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return getStorage().getItem(REFRESH_KEY);
}

export function getStoredRole(): string | null {
  if (typeof window === "undefined") return null;
  return getStorage().getItem(ROLE_KEY);
}

export function setSession(
  tokens: { access: string; refresh: string },
  role?: string,
  rememberMe: boolean = true
) {
  if (typeof window === "undefined") return;

  localStorage.setItem(REMEMBER_KEY, rememberMe ? "1" : "0");
  const storage = rememberMe ? localStorage : sessionStorage;

  storage.setItem(ACCESS_KEY, tokens.access);
  storage.setItem(REFRESH_KEY, tokens.refresh);

  if (role) {
    storage.setItem(ROLE_KEY, role);
    document.cookie = `qalajob-role=${role}; path=/; max-age=604800; SameSite=Lax`;
  }

  document.cookie = `qalajob-auth=1; path=/; max-age=604800; SameSite=Lax`;
}

export function clearSession() {
  if (typeof window === "undefined") return;

  // Clear both storages
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(ROLE_KEY);
  sessionStorage.removeItem(ACCESS_KEY);
  sessionStorage.removeItem(REFRESH_KEY);
  sessionStorage.removeItem(ROLE_KEY);

  document.cookie = "qalajob-auth=; path=/; max-age=0";
  document.cookie = "qalajob-role=; path=/; max-age=0";
}

/**
 * Parse JWT token to extract expiration.
 */
export function getTokenExpiration(token: string): number | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp ? payload.exp * 1000 : null;
  } catch {
    return null;
  }
}

/**
 * Check if access token is about to expire (within 2 minutes).
 */
export function isTokenExpiringSoon(): boolean {
  const token = getAccessToken();
  if (!token) return true;

  const exp = getTokenExpiration(token);
  if (!exp) return true;

  return Date.now() > exp - 2 * 60 * 1000;
}

/**
 * Check if access token has expired.
 */
export function isTokenExpired(): boolean {
  const token = getAccessToken();
  if (!token) return true;

  const exp = getTokenExpiration(token);
  if (!exp) return true;

  return Date.now() > exp;
}
