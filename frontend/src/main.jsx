import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import coverTextureUrl from './assets/cover-texture.jpg'
import './index.css'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'

document.documentElement.style.setProperty(
  '--cover-texture',
  `url("${coverTextureUrl}")`,
)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
