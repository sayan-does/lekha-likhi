import React, { useLayoutEffect, useRef } from 'react';
import PaperSurface from './PaperSurface';
import SharePopover from './SharePopover';
import styles from './JournalPage.module.css';

export default function JournalPage({
  dateLabel,
  body = '',
  isEditMode = false,
  autoFocus = false,
  pageSeed,
  onChange,
  emptyPrompt,
  shareControls,
  initialCaret = null,
  initialScrollTop = 0,
  onCaretChange,
  onScrollChange,
}) {
  const shareAnchorRef = useRef(null);
  const editorRef = useRef(null);
  const restoredSeed = useRef(null);
  const text = body ?? '';
  const hasDate = Boolean(dateLabel);
  const isEmpty = text.length === 0;
  const showPrompt = !isEditMode && isEmpty && Boolean(emptyPrompt);

  const {
    isOpen = false,
    onToggle,
    onClose,
    hasLink = false,
    reactionCount = 0,
    shareToken = null,
    copied = false,
    onShare,
    groups = [],
    selected = null,
    onReactionSelect,
  } = shareControls ?? {};

  useLayoutEffect(() => {
    if (!isEditMode) return;
    const editor = editorRef.current;
    if (!editor) return;
    if (restoredSeed.current === pageSeed) return;
    restoredSeed.current = pageSeed;

    if (initialCaret && Number.isFinite(initialCaret.start)) {
      const start = Math.max(0, Math.min(initialCaret.start, editor.value.length));
      const end = Math.max(
        start,
        Math.min(initialCaret.end ?? initialCaret.start, editor.value.length),
      );
      editor.setSelectionRange(start, end);
    }
  }, [isEditMode, pageSeed, initialCaret, text]);

  function reportCaret(event) {
    onCaretChange?.({
      start: event.target.selectionStart,
      end: event.target.selectionEnd,
    });
  }

  return (
    <PaperSurface
      pageSeed={pageSeed}
      initialScrollTop={isEditMode ? initialScrollTop : 0}
      onScrollChange={isEditMode ? onScrollChange : undefined}
    >
      <div className={styles.page}>
        {hasDate ? (
          <div className={styles.dateRow}>
            <p className={`headline-md ${styles.date}`}>{dateLabel}</p>
            {shareControls ? (
              <div className={styles.shareAnchor} ref={shareAnchorRef}>
                <button
                  type="button"
                  data-share-stamp
                  className={`${styles.shareStamp}${hasLink ? ` ${styles.hasLink}` : ''}`}
                  onClick={onToggle}
                  aria-expanded={isOpen}
                  aria-label="Share entry"
                >
                  <span className={`label-sm ${styles.shareStampLabel}`}>share</span>
                  {hasLink ? <span className={styles.linkDot} aria-hidden="true" /> : null}
                  {reactionCount > 0 ? (
                    <span className={styles.reactionBadge} aria-label={`${reactionCount} reactions`}>
                      {reactionCount}
                    </span>
                  ) : null}
                </button>
                <SharePopover
                  isOpen={isOpen}
                  onClose={onClose}
                  anchorRef={shareAnchorRef}
                  shareToken={shareToken}
                  copied={copied}
                  onShare={onShare}
                  groups={groups}
                  selected={selected}
                  onSelect={onReactionSelect}
                />
              </div>
            ) : null}
          </div>
        ) : null}

        {isEditMode ? (
          <textarea
            ref={editorRef}
            className={`body-lg ${styles.editor}`}
            value={text}
            onChange={(event) => onChange?.(event.target.value)}
            onSelect={reportCaret}
            aria-label={dateLabel || 'Journal entry'}
            spellCheck={false}
            autoFocus={autoFocus}
          />
        ) : (
          <div className={`body-lg ${styles.body}`}>
            {showPrompt ? (
              <span className={styles.prompt}>{emptyPrompt}</span>
            ) : (
              text
            )}
          </div>
        )}
      </div>
    </PaperSurface>
  );
}
