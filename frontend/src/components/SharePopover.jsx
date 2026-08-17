import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import ReactionBar from './ReactionBar';
import styles from './SharePopover.module.css';

export default function SharePopover({
  isOpen,
  onClose,
  anchorRef,
  shareToken,
  copied,
  onShare,
  groups,
  selected,
  onSelect,
}) {
  const popoverRef = useRef(null);
  const [position, setPosition] = useState(null);

  useEffect(() => {
    if (!isOpen || !anchorRef?.current) {
      setPosition(null);
      return undefined;
    }

    function updatePosition() {
      const anchor = anchorRef.current;
      if (!anchor) return;
      const rect = anchor.getBoundingClientRect();
      setPosition({
        top: rect.bottom + 6,
        left: Math.min(rect.right, window.innerWidth - 16),
      });
    }

    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition, true);
    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition, true);
    };
  }, [isOpen, anchorRef]);

  useEffect(() => {
    if (!isOpen) return undefined;

    function handlePointerDown(event) {
      if (popoverRef.current?.contains(event.target)) return;
      if (anchorRef?.current?.contains(event.target)) return;
      onClose();
    }

    document.addEventListener('pointerdown', handlePointerDown);
    return () => document.removeEventListener('pointerdown', handlePointerDown);
  }, [isOpen, onClose, anchorRef]);

  if (!isOpen || !position) return null;

  return createPortal(
    <div
      className={styles.popover}
      ref={popoverRef}
      role="dialog"
      aria-label="Share entry"
      style={{
        position: 'fixed',
        top: position.top,
        left: position.left,
        transform: 'translateX(-100%)',
      }}
    >
      <button
        type="button"
        className={`${styles.shareAction}${copied ? ` ${styles.copied}` : ''}`}
        onClick={onShare}
      >
        <span className={`label-sm ${styles.shareLabel}`}>
          {copied ? 'copied!' : shareToken ? 'copy link' : 'share link'}
        </span>
        {copied ? <span className={styles.inkDot} aria-hidden="true" /> : null}
      </button>
      <ReactionBar
        groups={groups}
        selected={selected}
        onSelect={onSelect}
        disabled={!shareToken}
        embedded
      />
    </div>,
    document.body,
  );
}
