import React, { useState, useRef, useEffect } from 'react';

export default function JournalPage({ initialEntry, dateLabel, isEditMode = true, pageSeed }) {
  const [content, setContent] = useState(initialEntry || '');
  const [saveIndicator, setSaveIndicator] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
    
    if (isEditMode) {
      // Mock autosave
      const timer = setTimeout(() => {
        setSaveIndicator(true);
        setTimeout(() => setSaveIndicator(false), 1500);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [content, isEditMode]);

  return (
    <div className="w-full flex-grow relative pb-24 max-w-2xl mx-auto writing-mode-bg">
      <svg aria-hidden="true" focusable="false" style={{ width: 0, height: 0, position: 'absolute' }}>
        <defs>
          <filter height="110%" id="torn-filter" width="110%" x="-5%" y="-5%">
            <feTurbulence baseFrequency="0.04" numOctaves="3" result="noise" type="fractalNoise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" result="displaced" scale="8" xChannelSelector="R" yChannelSelector="G" />
            <feGaussianBlur in="displaced" result="blurred" stdDeviation="0.5" />
            <feComposite in="blurred" in2="SourceGraphic" operator="in" />
          </filter>
        </defs>
      </svg>
      <article className="paper-texture torn-edge-filter w-full min-h-[707px] shadow-[0_20px_40px_-10px_rgba(217,197,160,0.4),0_0_20px_rgba(0,0,0,0.5)] rounded-sm relative overflow-hidden flex flex-col">
        {/* Left Margin Line */}
        <div className="absolute left-[15%] top-0 bottom-0 w-[1px] bg-tertiary-fixed-dim/40 z-0"></div>
        <div className="absolute left-[15.5%] top-0 bottom-0 w-[1px] bg-tertiary-fixed-dim/20 z-0"></div>
        
        <div className="writing-ruled-lines w-full flex-grow relative z-10 pt-[32px] px-page-margin pb-[32px]">
          {/* Date Header */}
          <header className="w-full text-right mb-[32px] pr-4 flex justify-end items-center gap-2">
            {saveIndicator && <span className="text-secondary opacity-50 font-handwriting">✓ saved</span>}
            <span className="font-headline-md text-headline-md text-surface-tint italic mr-4">{dateLabel || 'Today'}</span>
          </header>
          
          {/* Content Area */}
          <div className="pl-[12%] pr-4 pt-[2px] jitter-x relative">
            {isEditMode ? (
              <textarea
                ref={textareaRef}
                className="w-full bg-transparent resize-none outline-none font-body-lg text-body-lg ink-text leading-[32px] tracking-wide text-justify"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Begin writing..."
                spellCheck={false}
              />
            ) : (
              <div className="font-body-lg text-body-lg ink-text leading-[32px] tracking-wide text-justify whitespace-pre-wrap">
                {content}
              </div>
            )}
            {/* Blinking Cursor Simulation for focus could be added here if needed */}
          </div>
        </div>
      </article>
    </div>
  );
}
