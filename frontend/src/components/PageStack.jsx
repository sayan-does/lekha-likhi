import React, { useRef, useState } from 'react';
import JournalPage from './JournalPage';
import styles from './PageStack.module.css';

const DATE_FORMAT = { month: 'long', day: 'numeric' };

function formatEntryDate(iso) {
  const [year, month, day] = iso.split('-').map(Number);
  return new Intl.DateTimeFormat(undefined, DATE_FORMAT).format(
    new Date(year, month - 1, day),
  );
}

const SWIPE_THRESHOLD = 50;
const DRAG_LOCK = 8;

export default function PageStack({
  entries,
  activeIndex,
  onIndexChange,
  onEntryChange,
  autoFocusId,
}) {
  const containerRef = useRef(null);
  const pointerRef = useRef(null);
  const [dragX, setDragX] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  function resetDrag() {
    pointerRef.current = null;
    setIsDragging(false);
    setDragX(0);
  }

  function onPointerDown(event) {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    if (event.target.closest('button')) return;

    pointerRef.current = {
      id: event.pointerId,
      x: event.clientX,
      y: event.clientY,
      locked: false,
      fromField: Boolean(event.target.closest('textarea, input')),
    };
  }

  function onPointerMove(event) {
    const pointer = pointerRef.current;
    if (!pointer || event.pointerId !== pointer.id) return;
    if (pointer.fromField) return;

    const dx = event.clientX - pointer.x;
    const dy = event.clientY - pointer.y;

    if (!pointer.locked) {
      if (Math.abs(dx) < DRAG_LOCK && Math.abs(dy) < DRAG_LOCK) return;
      if (Math.abs(dx) <= Math.abs(dy)) {
        pointerRef.current = null;
        return;
      }
      pointer.locked = true;
      event.currentTarget.setPointerCapture(event.pointerId);
      setIsDragging(true);
    }

    setDragX(dx);
  }

  function onPointerUp(event) {
    const pointer = pointerRef.current;
    if (!pointer || event.pointerId !== pointer.id) {
      resetDrag();
      return;
    }

    const dx = event.clientX - pointer.x;
    const locked = pointer.locked;
    resetDrag();

    if (!locked) return;

    if (dx < -SWIPE_THRESHOLD && activeIndex < entries.length - 1) {
      onIndexChange(activeIndex + 1);
      return;
    }

    if (dx > SWIPE_THRESHOLD && activeIndex > 0) {
      onIndexChange(activeIndex - 1);
    }
  }

  const width = containerRef.current?.clientWidth || 1;
  const progress = Math.max(-1, Math.min(1, dragX / (width * 0.42)));

  return (
    <div
      className={`${styles.perspectiveContainer}${isDragging ? ` ${styles.dragging}` : ''}`}
      ref={containerRef}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={resetDrag}
    >
      {entries.map((entry, index) => {
        if (Math.abs(index - activeIndex) > 1) return null;

        let pageState = 'active';
        if (index < activeIndex) pageState = 'past';
        if (index > activeIndex) pageState = 'future';

        const inlineStyle = { zIndex: entries.length - index };

        if (isDragging) {
          if (index === activeIndex && progress < 0) {
            inlineStyle.transform = `rotateY(${progress * 100}deg)`;
          } else if (index === activeIndex - 1 && progress > 0) {
            inlineStyle.transform = `rotateY(${-100 + progress * 100}deg)`;
            inlineStyle.opacity = String(0.35 + progress * 0.65);
          }
        }

        return (
          <div
            key={entry.id}
            className={`${styles.pageWrapper} ${styles[pageState]}`}
            style={inlineStyle}
          >
            <JournalPage
              body={entry.content}
              dateLabel={formatEntryDate(entry.date)}
              pageSeed={entry.id}
              isEditMode={index === activeIndex}
              autoFocus={entry.id === autoFocusId}
              onChange={(content) => onEntryChange(index, content)}
            />
          </div>
        );
      })}
    </div>
  );
}
