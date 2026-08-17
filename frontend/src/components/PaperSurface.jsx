import React from 'react';
import styles from './PaperSurface.module.css';

function hashSeed(seed) {
  const str = String(seed);
  let h = 0;
  for (let i = 0; i < str.length; i += 1) {
    h = (h * 31 + str.charCodeAt(i)) | 0;
  }
  return Math.abs(h);
}

function sanitizeSeed(seed) {
  const raw = String(seed);
  const escaped = typeof CSS !== 'undefined' && CSS.escape ? CSS.escape(raw) : raw;
  const cleaned = escaped.replace(/[^a-zA-Z0-9_-]/g, '_') || 'page';
  return /^[A-Za-z_]/.test(cleaned) ? cleaned : `p_${cleaned}`;
}

export default function PaperSurface({ children, pageSeed = 'default', className }) {
  const hash = hashSeed(pageSeed);
  const safeId = sanitizeSeed(pageSeed);
  const jitterX = ((hash % 2) + 1) * (hash % 3 === 0 ? -1 : 1);
  const ruleOffset = hash % 3;
  const grainX = (hash >>> 3) % 24;
  const grainY = (hash >>> 7) % 24;

  return (
    <div
      className={[styles.root, className].filter(Boolean).join(' ')}
      id={`paper-${safeId}`}
      style={{
        '--jitter-x': `${jitterX}px`,
        '--rule-offset': `${ruleOffset}px`,
        '--grain-x': `${grainX}px`,
        '--grain-y': `${grainY}px`,
      }}
    >
      <div className={styles.paper}>
        <div className={styles.scroll}>
          <div className={styles.content}>
            <div className={styles.margin} aria-hidden="true" />
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
