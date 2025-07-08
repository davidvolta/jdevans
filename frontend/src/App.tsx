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
  const [error, setError] = useState<string | null>(null)
  const isMobile = useIsMobile()

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || '';
    fetch(`${apiUrl}/poems`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch poems')
        return res.json()
      })
      .then(data => {
        setPoems(data.poems)
      })
      .catch(err => {
        setError(err.message)
      })
  }, [])

  const handlePoemGenerated = (newPoem: Poem & { content: string; signature?: string }) => {
    setPoems(prevPoems => [newPoem, ...prevPoems]);
  };

  if (error) {
    return (
      <div className="loading error">
        <span>Error: {error}</span>
      </div>
    )
  }

  return (
    <BrowserRouter>
      {isMobile ? 
        <MobileLayout poems={poems} onPoemGenerated={handlePoemGenerated} /> : 
        <DesktopLayout poems={poems} onPoemGenerated={handlePoemGenerated} />
      }
    </BrowserRouter>
  )
}

export default App
