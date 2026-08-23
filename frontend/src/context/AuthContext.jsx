import React, { createContext, useContext, useEffect, useState } from 'react';
import { getApiUrl } from '../api/config';
import { setTokenGetter } from '../api/client';
import { clearWritingSession } from '../utils/writingSession';

const AuthContext = createContext(null);

const STORAGE_KEY = 'access_token';

const AUTH_ERROR_MESSAGES = {
  google_denied: 'Google sign-in was cancelled. Try again.',
  google_token: 'Google sign-in did not complete. Try again.',
  google_profile: 'Google did not share an email for this account.',
  db_error: 'Could not save your account. Try again in a moment.',
  unknown: 'Sign-in failed. Try again.',
};

function parseHashParams() {
  const hash = window.location.hash;
  if (!hash || hash.length < 2) return new URLSearchParams();
  return new URLSearchParams(hash.slice(1));
}

function messageForAuthError(code) {
  if (!code) return null;
  return AUTH_ERROR_MESSAGES[code] || AUTH_ERROR_MESSAGES.unknown;
}

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null);
  const [user, setUser] = useState(null);
  const [isReady, setIsReady] = useState(false);
  const [loginError, setLoginError] = useState(null);

  useEffect(() => {
    const params = parseHashParams();
    const fromHash = params.get('access_token');
    const hashError = params.get('auth_error');
    if (fromHash || hashError) {
      window.history.replaceState(null, '', window.location.pathname);
    }
    if (fromHash) {
      sessionStorage.setItem(STORAGE_KEY, fromHash);
      setAccessToken(fromHash);
    } else {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) setAccessToken(stored);
    }
    if (hashError) setLoginError(messageForAuthError(hashError));
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
    setLoginError(null);
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
      value={{ accessToken, user, isReady, isAuthenticated: Boolean(accessToken), login, loginError, logout }}
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
