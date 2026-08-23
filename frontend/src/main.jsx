import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { registerSW } from 'virtual:pwa-register'
import coverTextureUrl from './assets/cover-texture.jpg'
import rajnigandhaFontUrl from './assets/fonts/Rajnigandha/Rajnigandha ANSI.ttf?url'
import './index.css'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'

registerSW({ immediate: true })

document.documentElement.style.setProperty(
  '--cover-texture',
  `url("${coverTextureUrl}")`,
)

if (!document.querySelector('[data-preload-rajnigandha]')) {
  const preload = document.createElement('link')
  preload.rel = 'preload'
  preload.as = 'font'
  preload.type = 'font/ttf'
  preload.crossOrigin = 'anonymous'
  preload.href = rajnigandhaFontUrl
  preload.dataset.preloadRajnigandha = ''
  document.head.appendChild(preload)
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
