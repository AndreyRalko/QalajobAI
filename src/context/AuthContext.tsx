"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  useRef,
  type ReactNode,
} from "react";

import { getMe, logoutApi, type ApiUser } from "@/lib/api";
import {
  clearSession,
  getAccessToken,
  getRefreshToken,
  getStoredRole,
  isTokenExpiringSoon,
} from "@/lib/session";

type AuthContextType = {
  user: ApiUser | null;
  role: string | null;
  loading: boolean;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  role: null,
  loading: true,
  logout: async () => {},
  refreshUser: async () => {},
});

const REFRESH_INTERVAL_MS = 4 * 60 * 1000; // Check every 4 minutes

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<ApiUser | null>(null);
  const [role, setRole] = useState<string | null>(getStoredRole());
  const [loading, setLoading] = useState(true);
  const refreshIntervalRef = useRef<ReturnType<typeof setInterval> | null>(
    null
  );

  const logout = useCallback(async () => {
    try {
      const refresh = getRefreshToken();
      if (refresh) {
        await logoutApi(refresh).catch(() => {});
      }
    } finally {
      clearSession();
      setUser(null);
      setRole(null);
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
  }, []);

  const refreshUser = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;

    try {
      const me = await getMe(token);
      setUser(me);
      setRole(me.role);
    } catch {
      // Token invalid, will be refreshed on next API call
    }
  }, []);

  useEffect(() => {
    const loadUser = async () => {
      const token = getAccessToken();

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const me = await getMe();
        setUser(me);
        setRole(me.role);
      } catch {
        clearSession();
      } finally {
        setLoading(false);
      }
    };

    loadUser();

    // Set up periodic token check
    refreshIntervalRef.current = setInterval(() => {
      const token = getAccessToken();
      if (!token) {
        // User logged out elsewhere
        setUser(null);
        setRole(null);
        return;
      }

      if (isTokenExpiringSoon()) {
        // The API client will auto-refresh on next request
        refreshUser();
      }
    }, REFRESH_INTERVAL_MS);

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [refreshUser]);

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        loading,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}