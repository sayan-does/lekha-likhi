import React from 'react';
import styles from './PaperSurface.module.css';

export default function PaperSurface({ children, pageSeed = 'default' }) {
  // Use pageSeed to slightly offset background and add micro-jitter
  // Convert string/number seed to a simple hash for jitter
  const hash = typeof pageSeed === 'string' ? pageSeed.length : pageSeed;
  const customStyles = {
    '--jitter-x': `${(hash % 3) - 1}px`,
    filter: `url(#torn-edge-${pageSeed})`,
  };

  return (
    <div className={styles.paperWrapper} style={{ transform: `translateX(${customStyles['--jitter-x']})` }}>
      {/* SVG filter for torn edges - defined per surface to allow variation if needed */}
      <svg width="0" height="0" className={styles.svgFilter}>
        <filter id={`torn-edge-${pageSeed}`} x="-5%" y="-5%" width="110%" height="110%">
          {/* Base frequency variations could be tied to seed in the future */}
          <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" result="noise" />
          {/* Jagged on Y axis mostly to keep side binding straighter, but we'll apply equally first */}
          <feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="G" />
        </filter>
      </svg>
      
      <div className={styles.paperSurface} style={{ filter: customStyles.filter }}>
        <div className={styles.paperRuledLines}>
          <div className={styles.paperContent}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
