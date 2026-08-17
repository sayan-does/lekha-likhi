import React, { useState } from 'react';

export default function Dashboard() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="bg-surface-dim min-h-screen text-on-surface font-body-md overflow-x-hidden selection:bg-[#F0E68C] selection:text-on-surface">
      {/* SVG Filters for Ink and Torn effects */}
      <svg aria-hidden="true" focusable="false" style={{ width: 0, height: 0, position: 'absolute' }}>
        <filter id="ink-bleed-filter">
          <feTurbulence baseFrequency="0.05" numOctaves="3" result="noise" type="fractalNoise" />
          <feDisplacementMap in="SourceGraphic" in2="noise" scale="2" xChannelSelector="R" yChannelSelector="G" />
        </filter>
      </svg>

      {/* App Container (Fluid Grid) */}
      <div className="relative w-full max-w-3xl mx-auto min-h-screen flex flex-col pt-8 pb-20 px-page-margin">
        
        {/* TopAppBar */}
        <header className="flex justify-between items-center w-full px-page-margin border-b border-outline-variant bg-surface top-0 pt-8 pb-4 shadow-[4px_4px_0px_0px_rgba(217,197,160,0.3)] sticky z-50">
          <div className="flex items-center gap-4">
            <button 
              className="text-on-surface-variant hover:opacity-80 transition-opacity active:translate-x-[1px] active:translate-y-[1px] transition-transform md:hidden"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            >
              <span className="material-symbols-outlined">menu</span>
            </button>
            <h1 className="font-headline-md text-headline-md font-bold tracking-tight text-primary">October 24, 1952</h1>
          </div>
          <div className="flex items-center gap-4">
            <button className="text-on-surface-variant hover:opacity-80 transition-opacity active:translate-x-[1px] active:translate-y-[1px] transition-transform">
              <span className="material-symbols-outlined">edit</span>
            </button>
          </div>
        </header>

        {/* Main Canvas: Page Turn Interaction */}
        <main className="relative flex-grow mt-8" style={{ perspective: '1000px' }}>
          {/* Next Page (Underneath) */}
          <div className="absolute inset-0 bg-surface paper-texture ruled-lines torn-edge shadow-md p-6 z-0 transform translate-x-2 translate-y-1 rotate-1 opacity-80">
            <div className="font-handwriting text-2xl text-secondary opacity-50 pl-4 pt-12">
              <p>October 23...</p>
              <p className="mt-line-height-unit">Arrived in the port city before dawn. The mist was thick, clinging to the cobblestones.</p>
              <p className="mt-line-height-unit">Met the contact at the usual cafe. He seemed nervous.</p>
            </div>
          </div>

          {/* Current Page (Lifting) */}
          <div className="absolute inset-0 bg-surface paper-texture ruled-lines torn-edge shadow-xl p-6 z-10 transform origin-left transition-transform duration-500 hover:rotate-y-[-5deg]">
            <div className="font-handwriting text-3xl text-primary pl-4 pt-2 leading-[32px] ink-bleed">
              <p className="mt-[32px]">The train ride was long, but the views of the countryside were worth the discomfort.</p>
              
              <div className="mt-[64px] mb-[32px] w-3/4 mx-auto relative transform -rotate-2 p-2 bg-surface-container-low shadow-sm border border-outline-variant/30">
                <img 
                  className="w-full h-auto object-cover opacity-90 sepia-[0.3]" 
                  alt="A vintage, sepia-toned photograph of a steam train crossing a stone viaduct over a lush valley." 
                  src="https://images.unsplash.com/photo-1474487548417-781cb71495f3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" 
                />
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-12 h-4 bg-surface-variant opacity-60 transform rotate-3"></div> {/* Tape */}
              </div>

              <p className="mt-[32px]">I finally unpacked the sketches from Florence. They survived the journey better than I did.</p>
              <p className="mt-[32px]">Need to find more ink tomorrow.</p>
            </div>
            
            {/* Curl Effect overlay */}
            <div className="page-curl"></div>
          </div>
        </main>

        {/* Floating Action Button */}
        <button className="fixed bottom-24 right-8 w-16 h-16 rounded-full border-2 border-primary bg-surface flex items-center justify-center shadow-lg hover:shadow-xl active:translate-x-[1px] active:translate-y-[1px] transition-all z-50 ink-bleed-element">
          <span className="material-symbols-outlined text-primary text-3xl font-bold" style={{ fontVariationSettings: "'wght' 700" }}>add</span>
        </button>

        {/* BottomNavBar */}
        <nav className="md:hidden fixed bottom-0 left-0 w-full flex justify-around items-center px-4 pb-4 bg-surface-container border-t-2 border-dashed border-outline-variant h-20 z-50 rounded-t-xl shadow-[0_-4px_10px_rgba(217,197,160,0.2)]">
          <a href="#" className="text-on-surface-variant p-3 hover:bg-surface-variant rounded-full active:scale-95 duration-100 flex flex-col items-center gap-1">
            <span className="material-symbols-outlined">book</span>
          </a>
          <a href="#" className="text-on-surface-variant p-3 hover:bg-surface-variant rounded-full active:scale-95 duration-100 flex flex-col items-center gap-1">
            <span className="material-symbols-outlined">history</span>
          </a>
          <a href="#" className="bg-tertiary-fixed text-on-tertiary-fixed-variant rounded-full p-3 shadow-inner active:scale-95 duration-100 flex flex-col items-center gap-1">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>search</span>
          </a>
          <a href="#" className="text-on-surface-variant p-3 hover:bg-surface-variant rounded-full active:scale-95 duration-100 flex flex-col items-center gap-1">
            <span className="material-symbols-outlined">settings</span>
          </a>
        </nav>
      </div>

      {/* Desktop Navigation Drawer */}
      <aside className={`md:flex flex-col h-full py-8 gap-4 bg-surface-container-low shadow-2xl h-screen w-80 rounded-r-xl border-r border-outline-variant fixed top-0 left-0 z-40 transform transition-transform duration-300 ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        {/* Header Profile */}
        <div className="px-6 mb-8 flex items-center gap-4">
          <img 
            className="w-16 h-16 rounded-full border border-outline-variant object-cover grayscale" 
            alt="The Traveler" 
            src="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80" 
          />
          <div>
            <h2 className="font-display-lg text-display-lg text-primary text-xl font-bold">The Traveler</h2>
            <p className="font-body-md text-sm text-on-surface-variant">Last entry: 2 days ago</p>
          </div>
        </div>

        {/* Nav Items */}
        <nav className="flex flex-col gap-2 font-body-lg text-body-lg">
          <a href="#" className="flex items-center gap-3 font-bold text-primary bg-secondary-container/50 rounded-lg mx-2 p-3 hover:bg-secondary-container/30 transition-colors active:translate-x-1 duration-150">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>auto_stories</span>
            Daily Entries
          </a>
          <a href="#" className="flex items-center gap-3 text-on-surface-variant mx-2 p-3 hover:bg-secondary-container/30 transition-colors active:translate-x-1 duration-150">
            <span className="material-symbols-outlined">map</span>
            Travel Logs
          </a>
          <a href="#" className="flex items-center gap-3 text-on-surface-variant mx-2 p-3 hover:bg-secondary-container/30 transition-colors active:translate-x-1 duration-150">
            <span className="material-symbols-outlined">brush</span>
            Sketches
          </a>
          <a href="#" className="flex items-center gap-3 text-on-surface-variant mx-2 p-3 hover:bg-secondary-container/30 transition-colors active:translate-x-1 duration-150">
            <span className="material-symbols-outlined">inventory_2</span>
            Archived Notes
          </a>
        </nav>

        <div className="mt-auto">
          <a href="#" className="flex items-center gap-3 text-on-surface-variant mx-2 p-3 hover:bg-secondary-container/30 transition-colors active:translate-x-1 duration-150">
            <span className="material-symbols-outlined">settings</span>
            Settings
          </a>
        </div>
      </aside>
    </div>
  );
}
