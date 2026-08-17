import React from 'react';
import FallingLeaves from './FallingLeaves';
import styles from './CoverShell.module.css';

export default function CoverShell({ children, className, contentClassName }) {
  return (
    <div className={['cover', className].filter(Boolean).join(' ')}>
      <FallingLeaves />
      <div className={[styles.content, contentClassName].filter(Boolean).join(' ')}>
        {children}
      </div>
    </div>
  );
}
