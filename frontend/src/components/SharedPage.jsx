import React from 'react';
import { useParams } from 'react-router-dom';

export default function SharedPage() {
  const { token } = useParams();

  return (
    <div className="shared-bg min-h-screen flex flex-col items-center py-8 px-4 md:px-page-margin overflow-x-hidden font-body-lg text-on-surface">
      {/* Top Navigation Area */}
      <header className="w-full max-w-3xl flex justify-between items-center px-page-margin pt-8 pb-4 border-b border-outline-variant bg-surface mb-8 shadow-[4px_4px_0px_0px_rgba(217,197,160,0.3)] torn-edge-bottom paper-grain z-20 sticky top-4">
        <button className="text-on-surface-variant hover:opacity-80 transition-opacity active:translate-x-[1px] active:translate-y-[1px] transition-transform">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>arrow_back</span>
        </button>
        <div className="text-center flex-1">
          <h1 className="font-headline-md text-headline-md text-primary dark:text-primary-fixed">October 24, 1952</h1>
        </div>
        <div className="w-6 h-6"></div> {/* Spacer for centering */}
      </header>

      {/* Main Journal Content */}
      <main className="w-full max-w-3xl flex-1 relative z-10 pb-32">
        {/* The Paper Canvas */}
        <article className="paper-grain torn-edge-top torn-edge-bottom shadow-2xl shadow-secondary/50 w-full min-h-[530px] px-8 py-12 relative">
          {/* Ruled Lines Overlay */}
          <div className="absolute inset-0 shared-ruled-lines opacity-70 pointer-events-none mt-8"></div>
          
          <div className="relative z-10 space-y-[32px] mt-1 text-primary">
            <h2 className="font-display-lg text-display-lg italic shared-ink-bleed pl-2 transform -rotate-1">Arrival in Kyoto</h2>
            
            <p className="font-body-lg leading-[32px] shared-ink-bleed text-on-surface">
                The train ride was long, but watching the landscape shift from dense urban grids to mist-covered hills was entirely worth it. I found a small inn tucked away near an old shrine. The air here smells of damp cedar and woodsmoke.
            </p>

            {/* Polaroid/Scrap Photo Insert */}
            <div className="my-[64px] relative w-4/5 mx-auto transform rotate-2">
              <div className="bg-surface-container-lowest p-4 pb-12 shadow-md hand-drawn-border relative group cursor-pointer transition-transform duration-300 hover:rotate-1">
                {/* Washi Tape */}
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-24 h-8 bg-secondary-container/60 backdrop-blur-sm shadow-sm rotate-[-3deg] mix-blend-multiply opacity-80 z-20"></div>
                <img 
                  className="w-full h-auto object-cover grayscale sepia-[0.3] contrast-125 brightness-90 filter drop-shadow-sm" 
                  alt="A vintage black and white photograph of an old wooden shrine gate." 
                  src="https://images.unsplash.com/photo-1492571350019-22de08371fd3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" 
                />
                <p className="font-label-sm text-label-sm absolute bottom-4 right-4 text-secondary italic opacity-80 shared-ink-bleed">Near the eastern hills</p>
              </div>
            </div>

            <p className="font-body-lg leading-[32px] shared-ink-bleed text-on-surface">
                Met an old man sweeping the temple steps. He didn't speak much English, and my Japanese is terrible, but we shared a quiet moment watching a stray cat sleep on a stone lantern. I sketched it quickly in the margins before it woke up.
            </p>

            <p className="font-body-lg leading-[32px] shared-ink-bleed text-on-surface">
                Tomorrow, I plan to explore the philosopher's path. I need to buy more ink soon. This pen is starting to scratch.
            </p>

            {/* Little sketch element */}
            <div className="flex justify-end pr-8 pt-[32px] opacity-70">
              <span className="material-symbols-outlined text-[48px] text-primary" style={{ fontVariationSettings: "'FILL' 0", fontWeight: 200 }}>pets</span>
            </div>
          </div>
        </article>
      </main>

      {/* Fixed Reaction Bar */}
      <div className="fixed bottom-0 w-full max-w-3xl z-30 pb-4 px-page-margin">
        <div className="bg-surface-container-high torn-edge-top shadow-[0_-8px_20px_rgba(83,69,41,0.4)] px-6 pt-6 pb-4 flex items-center justify-between border-t-2 border-dashed border-outline-variant/30 paper-grain relative">
          {/* Users reacting */}
          <div className="flex items-center gap-3">
            <div className="flex -space-x-2">
              <img 
                className="w-8 h-8 rounded-full border border-surface object-cover shadow-sm grayscale sepia-[0.2]" 
                alt="Alice" 
                src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?ixlib=rb-4.0.3&auto=format&fit=crop&w=100&q=80" 
              />
              <img 
                className="w-8 h-8 rounded-full border border-surface object-cover shadow-sm grayscale sepia-[0.2]" 
                alt="Mark" 
                src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-4.0.3&auto=format&fit=crop&w=100&q=80" 
              />
              <div className="w-8 h-8 rounded-full bg-surface-variant border border-surface flex items-center justify-center shadow-sm">
                <span className="font-label-sm text-label-sm text-on-surface-variant">+2</span>
              </div>
            </div>
            <span className="font-label-sm text-label-sm italic text-on-surface-variant shared-ink-bleed">Alice, Mark &amp; 2 others</span>
          </div>

          {/* Reaction Actions */}
          <div className="flex gap-4">
            <button className="text-on-surface-variant hover:text-primary transition-colors active:translate-y-1">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>favorite</span>
            </button>
            <button className="text-on-surface-variant hover:text-primary transition-colors active:translate-y-1">
              <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 0" }}>draw</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
