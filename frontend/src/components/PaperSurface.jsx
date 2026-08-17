import React, { useLayoutEffect, useRef } from 'react';
import styles from './PaperSurface.module.css';

function hashSeed(seed) {
  const str = String(seed);
  let h = 0;
  for (let i = 0; i < str.length; i += 1) {
    h = (h * 31 + str.charCodeAt(i)) | 0;
  }
  return Math.abs(h);
}

export default function PaperSurface({
  children,
  pageSeed = 'default',
  className,
  initialScrollTop = 0,
  onScrollChange,
}) {
  const hash = hashSeed(pageSeed);
  const jitterX = ((hash % 2) + 1) * (hash % 3 === 0 ? -1 : 1);
  const ruleOffset = hash % 3;
  const grainX = (hash >>> 3) % 24;
  const grainY = (hash >>> 7) % 24;
  const stain1x = 6 + (hash % 18);
  const stain1y = 4 + ((hash >>> 2) % 16);
  const stain2x = 72 + ((hash >>> 5) % 20);
  const stain2y = 8 + ((hash >>> 8) % 22);
  const stain3x = 12 + ((hash >>> 11) % 28);
  const stain3y = 68 + ((hash >>> 14) % 22);
  const stain4x = 62 + ((hash >>> 17) % 26);
  const stain4y = 58 + ((hash >>> 20) % 28);
  const stain5x = 28 + ((hash >>> 4) % 44);
  const stain5y = 36 + ((hash >>> 9) % 28);
  const scrollRef = useRef(null);
  const restoredSeed = useRef(null);

  useLayoutEffect(() => {
    const node = scrollRef.current;
    if (!node) return;
    if (restoredSeed.current === pageSeed) return;
    restoredSeed.current = pageSeed;
    node.scrollTop = initialScrollTop || 0;
  }, [pageSeed, initialScrollTop]);

  return (
    <div
      className={[styles.root, className].filter(Boolean).join(' ')}
      style={{
        '--jitter-x': `${jitterX}px`,
        '--rule-offset': `${ruleOffset}px`,
        '--grain-x': `${grainX}px`,
        '--grain-y': `${grainY}px`,
        '--stain-1-x': `${stain1x}%`,
        '--stain-1-y': `${stain1y}%`,
        '--stain-2-x': `${stain2x}%`,
        '--stain-2-y': `${stain2y}%`,
        '--stain-3-x': `${stain3x}%`,
        '--stain-3-y': `${stain3y}%`,
        '--stain-4-x': `${stain4x}%`,
        '--stain-4-y': `${stain4y}%`,
        '--stain-5-x': `${stain5x}%`,
        '--stain-5-y': `${stain5y}%`,
      }}
    >
      <div className={styles.paper}>
        <div
          className={styles.scroll}
          ref={scrollRef}
          onScroll={
            onScrollChange
              ? (event) => onScrollChange(event.currentTarget.scrollTop)
              : undefined
          }
        >
          <div className={styles.content}>
            <div className={styles.margin} aria-hidden="true" />
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
