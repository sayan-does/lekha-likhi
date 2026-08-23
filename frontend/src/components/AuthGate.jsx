import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { backendUnreachableMessage, checkApiHealth, getApiUrl, isLocalApiUrl } from '../api/config';
import PaperSurface from './PaperSurface';
import CoverShell from './CoverShell';
import Logo from './Logo';
import styles from './AuthGate.module.css';

export default function AuthGate() {
  const { isAuthenticated, isReady, login, loginError } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const visibleError = error || loginError;

  const handleLogin = async () => {
    setError(null);
    setIsLoading(true);

    const apiUrl = getApiUrl();
    if (isLocalApiUrl(apiUrl)) {
      const healthy = await checkApiHealth();
      if (!healthy) {
        setError(backendUnreachableMessage());
        setIsLoading(false);
        return;
      }
    }

    login();
  };

  if (!isReady) {
    return null;
  }

  if (!isAuthenticated) {
    return (
      <CoverShell className={styles.shell} contentClassName={styles.shellContent}>
        <div className={styles.pageSlot}>
          <PaperSurface pageSeed="auth">
            <div className={styles.body}>
              <header className={styles.header}>
                <h1 className={styles.title}>
                  <Logo className={styles.logo} />
                </h1>
                <p className={`body-md ${styles.tagline}`}>
                  Open your notebook to begin writing.
                </p>
              </header>

              <div className={styles.actions}>
                <button
                  type="button"
                  aria-label="Sign in with Google"
                  aria-busy={isLoading}
                  className={styles.stamp}
                  onClick={handleLogin}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className={styles.scribble} aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none">
                        <path
                          className={styles.scribblePath}
                          d="M7.2 13.4c-.8-3.6 2.2-6.8 5.6-6.4 3.2.4 5.2 3.6 4.2 6.4-1.2 3.2-5.4 3.8-7.2 1.6-1.4-1.6-.4-4.2 1.8-4.8 2.2-.6 4.2.8 4.6 2.8"
                        />
                      </svg>
                    </span>
                  ) : (
                    <span className={styles.gMark} aria-hidden="true">
                      G
                    </span>
                  )}
                  <span className={`label-sm ${styles.stampLabel}`}>
                    Sign in with Google
                  </span>
                </button>
                {visibleError ? (
                  <p className={`body-md ${styles.error}`}>{visibleError}</p>
                ) : null}
              </div>
            </div>
          </PaperSurface>
        </div>
      </CoverShell>
    );
  }

  return <Outlet />;
}
