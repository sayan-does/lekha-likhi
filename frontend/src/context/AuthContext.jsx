import React, { createContext, useContext, useEffect, useState } from 'react';
import { getApiUrl } from '../api/config';
import { setTokenGetter } from '../api/client';
import { clearWritingSession } from '../utils/writingSession';

const AuthContext = createContext(null);

const STORAGE_KEY = 'access_token';

function parseHashToken() {
  const hash = window.location.hash;
  if (!hash.includes('access_token=')) return null;
  const params = new URLSearchParams(hash.slice(1));
  return params.get('access_token');
}

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null);
  const [user, setUser] = useState(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const fromHash = parseHashToken();
    if (fromHash) {
      sessionStorage.setItem(STORAGE_KEY, fromHash);
      window.history.replaceState(null, '', window.location.pathname);
      setAccessToken(fromHash);
    } else {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) setAccessToken(stored);
    }
    setIsReady(true);
  }, []);

  useEffect(() => {
    setTokenGetter(() => accessToken);
  }, [accessToken]);

  useEffect(() => {
    if (!accessToken) {
      setUser(null);
      return;
    }

    let cancelled = false;
    const apiUrl = getApiUrl();

    fetch(`${apiUrl}/me`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!cancelled && data) setUser(data);
      })
      .catch(() => {});

    return () => {
      cancelled = true;
    };
  }, [accessToken]);

  async function login() {
    const apiUrl = getApiUrl();
    const returnTarget = `${window.location.origin}${window.location.pathname}${window.location.search}`;
    const origin = encodeURIComponent(returnTarget);
    window.location.href = `${apiUrl}/auth/google/login?origin=${origin}`;
  }

  function logout() {
    sessionStorage.removeItem(STORAGE_KEY);
    clearWritingSession();
    setAccessToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{ accessToken, user, isReady, isAuthenticated: Boolean(accessToken), login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
