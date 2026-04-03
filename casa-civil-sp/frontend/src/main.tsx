import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App'
import './styles/theme.css'

// Em produção, VITE_API_URL aponta para o backend (ex: Render).
// Em desenvolvimento, as chamadas /api/... passam pelo proxy do Vite/Nginx.
const VITE_API_URL = import.meta.env.VITE_API_URL as string | undefined
if (VITE_API_URL) {
  axios.defaults.baseURL = VITE_API_URL
  // Axios ignora baseURL quando a URL começa com '/'; remove o slash inicial
  axios.interceptors.request.use(config => {
    if (config.url?.startsWith('/')) config.url = config.url.slice(1)
    return config
  })
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
