'use client'

import { useState, useEffect } from 'react'
import './globals.css'

interface GenerateResponse {
  title: string
  body: string
  signature: string
  similar_poems: string[]
}

interface ArchivePoem {
  id: number
  title: string
  content: string
  signature: string
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<'new' | 'archive'>('new')
  const [prompt, setPrompt] = useState('')
  const [poem, setPoem] = useState<GenerateResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [archivePoems, setArchivePoems] = useState<ArchivePoem[]>([])
  const [selectedArchivePoem, setSelectedArchivePoem] = useState<ArchivePoem | null>(null)
  const [showArchiveModal, setShowArchiveModal] = useState(false)

  // Load archive poems on component mount
  useEffect(() => {
    const loadArchivePoems = async () => {
      try {
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
        const response = await fetch(`${apiBaseUrl}/poems`);
        if (response.ok) {
          const data = await response.json();
          setArchivePoems(data);
        }
      } catch (err) {
        console.error('Failed to load archive poems:', err);
      }
    };
    
    loadArchivePoems();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim()) return
    setIsLoading(true)
    setError('')
    setPoem(null)
    setSelectedArchivePoem(null)

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${apiBaseUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: prompt.trim() }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: GenerateResponse = await response.json()
      setPoem(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const handleArchivePoemClick = (archivePoem: ArchivePoem) => {
    setSelectedArchivePoem(archivePoem)
    setPoem(null)
    setError('')
    setShowArchiveModal(false) // Close modal when poem is selected
  }

  const handleModalPoemClick = (archivePoem: ArchivePoem) => {
    setSelectedArchivePoem(archivePoem) // Set the selected poem
    setPoem(null)
    setError('')
    setShowArchiveModal(false) // Close modal when poem is selected
  }

  const handleTabClick = (tab: 'new' | 'archive') => {
    setActiveTab(tab)
    if (tab === 'archive') {
      setShowArchiveModal(true) // Show modal when archive tab is clicked
    } else {
      setShowArchiveModal(false) // Hide modal when new poem tab is clicked
      setSelectedArchivePoem(null) // Clear selected archive poem when switching to new poem tab
    }
  }

  const renderNewPoemTab = () => (
    <form
      className="prompt-form"
      onSubmit={handleSubmit}
    >
      <textarea
        className="prompt-textarea"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows={5}
        placeholder="Enter your prompt..."
      />
                <button
            type="submit"
            className="prompt-button"
            disabled={isLoading || !prompt.trim()}
          >
            Write
          </button>
    </form>
  )

  const renderArchiveTab = () => (
    <div className="archive-container">
      <div className="archive-list">
        {archivePoems.map((archivePoem) => (
          <div
            key={archivePoem.id}
            className="archive-poem-item"
            onClick={() => handleArchivePoemClick(archivePoem)}
          >
            <div className="archive-poem-title">{archivePoem.title}</div>
            <div className="archive-poem-id">#{archivePoem.id}</div>
          </div>
        ))}
      </div>
    </div>
  )

  return (
    <div className="layout">
      {/* Left column: fixed width, always visible */}
      <div className="left-column">
        <div className="tab-container">
          <div className="tab-header">
            <button
              className={`tab-button ${activeTab === 'new' ? 'active' : ''}`}
              onClick={() => handleTabClick('new')}
            >
              New Poem
            </button>
            <button
              className={`tab-button ${activeTab === 'archive' ? 'active' : ''}`}
              onClick={() => handleTabClick('archive')}
            >
              Archive
            </button>
          </div>
          <div className="tab-content">
            {activeTab === 'new' ? renderNewPoemTab() : renderArchiveTab()}
          </div>
        </div>
      </div>
      {/* Right column: scrollable, margin to avoid overlap with fixed left */}
      <div className="right-column">
        {(poem || selectedArchivePoem || isLoading || error) && (
          <div className="poem-display">
            {poem ? (
              <>
                <div className="poem-title">{poem.title}</div>
                <div className="poem-body">{poem.body}</div>
                {poem.signature && <div className="poem-signature">{poem.signature}</div>}
              </>
                      ) : selectedArchivePoem ? (
            <>
              <div className="poem-title">{selectedArchivePoem.title}</div>
              <div className="poem-body">{selectedArchivePoem.content}</div>
              {selectedArchivePoem.signature && <div className="poem-signature">{selectedArchivePoem.signature}</div>}
            </>

            ) : isLoading ? (
              <div className="loading">
                Generating your poem...
              </div>
            ) : error ? (
              <div className="error">
                Error: {error}
              </div>
            ) : null}
          </div>
        )}
      </div>
      
      {/* Mobile Archive Modal */}
      {showArchiveModal && (
        <div className="archive-modal-overlay">
          <div className="archive-modal">
            <div className="archive-modal-header">
              <h3>Archive</h3>
              <button 
                className="archive-modal-close"
                onClick={() => setShowArchiveModal(false)}
              >
                ×
              </button>
            </div>
            <div className="archive-modal-list">
              {archivePoems.map((archivePoem) => (
                <div
                  key={archivePoem.id}
                  className="archive-modal-poem-item"
                  onClick={() => handleModalPoemClick(archivePoem)}
                >
                  <div className="archive-modal-poem-title">{archivePoem.title}</div>
                  <div className="archive-modal-poem-id">#{archivePoem.id}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 