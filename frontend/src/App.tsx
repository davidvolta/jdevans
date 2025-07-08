import { useState, useEffect } from 'react'
import { BrowserRouter } from 'react-router-dom'
import MobileLayout from './MobileLayout'
import DesktopLayout from './DesktopLayout'
import type { Poem } from './PoemList'
import './App.css'

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)
  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])
  return isMobile
}

function App() {
  const [poems, setPoems] = useState<(Poem & { content: string; signature?: string })[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const isMobile = useIsMobile()

  useEffect(() => {
    fetch('/poems')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch poems')
        return res.json()
      })
      .then(data => {
        setPoems(data.poems)
        setIsLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setIsLoading(false)
      })
  }, [])

  if (isLoading) {
    return (
      <div className="loading">
        <img src="/loader.gif" alt="Loading..." className="loading-gif" />
        <span>Loading poems...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="loading error">
        <span>Error: {error}</span>
      </div>
    )
  }

  return (
    <BrowserRouter>
      {isMobile ? <MobileLayout poems={poems} /> : <DesktopLayout poems={poems} />}
    </BrowserRouter>
  )
}

export default App
