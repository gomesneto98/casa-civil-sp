import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Deputies from './pages/Deputies'
import Secretariats from './pages/Secretariats'
import Mayors from './pages/Mayors'
import Programs from './pages/Programs'

export default function App() {
  return (
    <BrowserRouter>
      <div className="main-layout">
        <Sidebar />
        <main className="page-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alesp" element={<Deputies />} />
            <Route path="/secretarias" element={<Secretariats />} />
            <Route path="/prefeitos" element={<Mayors />} />
            <Route path="/programas" element={<Programs />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
