import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Dashboard from './pages/Dashboard'
import Onboarding from './pages/Onboarding'
import Voice from './pages/Voice'
import Notes from './pages/Notes'
import Finance from './pages/Finance'
import Analytics from './pages/Analytics'
import FocusMode from './pages/FocusMode'
import { Button } from './components/Button'
import './styles/globals.css'

interface User {
  id: string
  email: string
  name: string
}

type PageType = 'login' | 'onboarding' | 'dashboard' | 'voice' | 'notes' | 'finance' | 'analytics' | 'focus'

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState<PageType>('login')

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token')
    if (token) {
      setCurrentPage('dashboard')
      setLoading(false)
    } else {
      setLoading(false)
    }
  }, [])

  const handleLogin = async () => {
    try {
      // For now, simulate login
      const mockUser = {
        id: '123',
        email: 'user@example.com',
        name: 'User',
      }
      setUser(mockUser)
      localStorage.setItem('access_token', 'mock-token')
      setCurrentPage('onboarding')
    } catch (err) {
      console.error('Login failed:', err)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
    setCurrentPage('login')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F4F4F0]">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-12 h-12 border-2 border-black"
        />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#F4F4F0] p-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <h1 className="text-5xl font-bold mb-4 font-[Archivo]">JARVIS</h1>
          <p className="text-xl text-[#666666] mb-2 font-[Inter]">
            AI-Powered Personal Event Manager
          </p>
          <p className="text-sm text-[#999999] mb-8 font-[Inter]">
            Savage PA & CFO Edition
          </p>
          
          <div className="bg-white border-2 border-black p-8 shadow-[4px_4px_0px_rgba(0,0,0,1)] max-w-md">
            <button
              onClick={handleLogin}
              className="w-full bg-black text-white border-2 border-black p-3 font-bold font-[Archivo] shadow-[2px_2px_0px_rgba(0,0,0,1)] hover:shadow-[4px_4px_0px_rgba(0,0,0,1)] hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all"
            >
              Sign in with Google
            </button>
          </div>
        </motion.div>
      </div>
    )
  }

  const navButtons: { label: string; page: PageType }[] = [
    { label: 'Dashboard', page: 'dashboard' },
    { label: 'Voice', page: 'voice' },
    { label: 'Finance', page: 'finance' },
    { label: 'Analytics', page: 'analytics' },
    { label: 'Focus', page: 'focus' },
    { label: 'Notes', page: 'notes' },
  ]

  return (
    <div className="min-h-screen bg-[#F4F4F0]">
      {/* Navigation */}
      <nav className="bg-white border-b-2 border-black shadow-[0_4px_0px_rgba(0,0,0,1)] sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center flex-wrap gap-2">
          <h1 className="text-2xl font-bold font-[Archivo]">JARVIS</h1>
          <div className="flex items-center gap-2 flex-wrap">
            {navButtons.map((btn) => (
              <button
                key={btn.page}
                onClick={() => setCurrentPage(btn.page)}
                className={`px-3 py-2 text-sm font-[Archivo] font-bold border-2 border-black transition-all ${
                  currentPage === btn.page
                    ? 'bg-black text-white'
                    : 'bg-white text-black hover:shadow-[2px_2px_0px_rgba(0,0,0,1)]'
                }`}
              >
                {btn.label}
              </button>
            ))}
            <button
              onClick={handleLogout}
              className="bg-white border-2 border-black px-3 py-2 text-sm font-bold font-[Archivo] shadow-[2px_2px_0px_rgba(0,0,0,1)] hover:shadow-[4px_4px_0px_rgba(0,0,0,1)] transition-all"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      {currentPage === 'onboarding' && <Onboarding />}
      {currentPage === 'dashboard' && <Dashboard />}
      {currentPage === 'voice' && <Voice />}
      {currentPage === 'notes' && <Notes />}
      {currentPage === 'finance' && <Finance />}
      {currentPage === 'analytics' && <Analytics />}
      {currentPage === 'focus' && <FocusMode />}
    </div>
  )
}

export default App
