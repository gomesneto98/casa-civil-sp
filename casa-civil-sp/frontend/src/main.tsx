import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App'
import './styles/theme.css'

// Em produção, VITE_API_URL aponta para o backend deployado.
// Em desenvolvimento, as chamadas /api/... passam pelo proxy do Vite/Nginx.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const apiUrl: string | undefined = (import.meta as any).env?.VITE_API_URL
if (apiUrl) {
  axios.defaults.baseURL = apiUrl
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
