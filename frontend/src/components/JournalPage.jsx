import React, { useLayoutEffect, useRef, useState } from 'react';
import PaperSurface from './PaperSurface';
import SharePopover from './SharePopover';
import {
  commitEditorNormalization,
  decodeAnsiDisplay,
  normalizeEditorText,
  toDisplayText,
  usesRajnigandha,
} from '../utils/bengaliFont';
import styles from './JournalPage.module.css';

function mapCaretToDisplay(raw, caret, displayText, bengaliInk) {
  if (!bengaliInk) return raw.slice(0, caret).length;
  if (raw.startsWith(displayText)) {
    const decodedBase = decodeAnsiDisplay(displayText);
    if (caret >= displayText.length) {
      return decodedBase.length + (caret - displayText.length);
    }
    return toDisplayText(decodeAnsiDisplay(raw.slice(0, caret))).length;
  }
  const prefix = raw.slice(0, caret);
  return toDisplayText(normalizeEditorText(prefix, { ansiMode: true })).length;
}

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
  const isComposingRef = useRef(false);
  const pendingCaretRef = useRef(null);
  const [composingValue, setComposingValue] = useState(null);
  const text = body ?? '';
  const bengaliInk = usesRajnigandha(text);
  const displayText = toDisplayText(text);
  const editorValue = composingValue !== null ? composingValue : displayText;
  const inkClass = bengaliInk ? styles.bengaliInk : undefined;
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

  function commitEditorChange(raw, caret) {
    const normalized = commitEditorNormalization(raw, displayText, bengaliInk);
    pendingCaretRef.current = {
      start: mapCaretToDisplay(raw, caret, displayText, bengaliInk),
      end: mapCaretToDisplay(raw, caret, displayText, bengaliInk),
    };
    onChange?.(normalized);
  }

  useLayoutEffect(() => {
    if (!isEditMode) return;
    const editor = editorRef.current;
    if (!editor) return;

    if (restoredSeed.current !== pageSeed) {
      restoredSeed.current = pageSeed;
      if (initialCaret && Number.isFinite(initialCaret.start)) {
        const start = Math.max(0, Math.min(initialCaret.start, editor.value.length));
        const end = Math.max(
          start,
          Math.min(initialCaret.end ?? initialCaret.start, editor.value.length),
        );
        editor.setSelectionRange(start, end);
        return;
      }
    }

    if (pendingCaretRef.current) {
      const { start, end } = pendingCaretRef.current;
      pendingCaretRef.current = null;
      const len = editor.value.length;
      editor.setSelectionRange(Math.min(start, len), Math.min(end ?? start, len));
    }
  }, [isEditMode, pageSeed, initialCaret, displayText]);

  function reportCaret(event) {
    onCaretChange?.({
      start: event.target.selectionStart,
      end: event.target.selectionEnd,
    });
  }

  function handleCompositionStart() {
    isComposingRef.current = true;
    setComposingValue(editorRef.current?.value ?? displayText);
  }

  function handleCompositionUpdate(event) {
    setComposingValue(event.target.value);
  }

  function handleCompositionEnd(event) {
    isComposingRef.current = false;
    setComposingValue(null);
    commitEditorChange(event.target.value, event.target.selectionStart);
  }

  function handleChange(event) {
    if (isComposingRef.current) {
      setComposingValue(event.target.value);
      return;
    }
    commitEditorChange(event.target.value, event.target.selectionStart);
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
            className={[styles.editor, inkClass].filter(Boolean).join(' ')}
            data-ink={bengaliInk ? 'bengali' : 'latin'}
            value={editorValue}
            onChange={handleChange}
            onCompositionStart={handleCompositionStart}
            onCompositionUpdate={handleCompositionUpdate}
            onCompositionEnd={handleCompositionEnd}
            onSelect={reportCaret}
            aria-label={dateLabel || 'Journal entry'}
            spellCheck={false}
            autoFocus={autoFocus}
          />
        ) : (
          <div
            className={[styles.body, inkClass].filter(Boolean).join(' ')}
            data-ink={bengaliInk ? 'bengali' : 'latin'}
          >
            {showPrompt ? (
              <span className={styles.prompt}>{emptyPrompt}</span>
            ) : (
              displayText
            )}
          </div>
        )}
      </div>
    </PaperSurface>
  );
}
