'use client'

import { useState, useEffect } from 'react'
import './globals.css'

interface GenerateResponse {
  title: string
  body: string
  signature: string
  similar_poems: string[]
  poem_id?: number
  illustration_prompt?: string
  illustration_url?: string
}

interface IllustrationResponse {
  status: string
  illustration_url?: string
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
  const [illustrationUrl, setIllustrationUrl] = useState<string | null>(null)
  const [isGeneratingImage, setIsGeneratingImage] = useState(false)
  const [is80sMode, setIs80sMode] = useState(false)

  // Load archive poems on component mount
  useEffect(() => {
    const loadArchivePoems = async () => {
      try {
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
        console.log('Loading archive poems from:', `${apiBaseUrl}/poems`);
        const response = await fetch(`${apiBaseUrl}/poems`);
        console.log('Archive response status:', response.status);
        if (response.ok) {
          const data = await response.json();
          console.log('Archive poems loaded:', data.poems?.length || 0);
          setArchivePoems(data.poems || []);
        } else {
          console.error('Failed to load archive poems. Status:', response.status);
        }
      } catch (err) {
        console.error('Failed to load archive poems:', err);
      }
    };
    
    loadArchivePoems();
  }, []);

  // Poll for illustration when user clicks generate image button
  const startImageGeneration = () => {
    if (!poem?.poem_id) return;

    setIsGeneratingImage(true);
    setIllustrationUrl(null);

    const interval = setInterval(async () => {
      try {
        const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
        const response = await fetch(`${apiBaseUrl}/illustration?poem_id=${poem.poem_id}`);
        if (response.ok) {
          const data: IllustrationResponse = await response.json();
          
          if (data.status === "ready") {
            setIllustrationUrl(data.illustration_url || null);
            setIsGeneratingImage(false);
            clearInterval(interval);
          }
        }
      } catch (err) {
        console.error('Failed to check illustration status:', err);
        setIsGeneratingImage(false);
        clearInterval(interval);
      }
    }, 3000); // poll every 3 seconds

    // Store the interval ID so we can clear it if needed
    return () => clearInterval(interval);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim()) return
    setIsLoading(true)
    setError('')
    setPoem(null)
    setSelectedArchivePoem(null)
    setIllustrationUrl(null)
    setIsGeneratingImage(false)

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${apiBaseUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          mode: is80sMode ? "1980s" : null
        }),
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
      setIs80sMode(false) // Deselect the checkbox when poem is complete
    }
  }

  const handleArchivePoemClick = (archivePoem: ArchivePoem) => {
    setSelectedArchivePoem(archivePoem)
    setPoem(null)
    setError('')
    setIllustrationUrl(null)
    setIsGeneratingImage(false)
    setShowArchiveModal(false) // Close modal when poem is selected
  }

  const handleModalPoemClick = (archivePoem: ArchivePoem) => {
    setSelectedArchivePoem(archivePoem) // Set the selected poem
    setPoem(null)
    setError('')
    setIllustrationUrl(null)
    setIsGeneratingImage(false)
    setShowArchiveModal(false) // Close modal when poem is selected
  }

  const handleTabClick = (tab: 'new' | 'archive') => {
    setActiveTab(tab)
    if (tab === 'archive') {
      setShowArchiveModal(true) // Show modal when archive tab is clicked
    } else {
      setShowArchiveModal(false) // Hide modal when new poem tab is clicked
      setSelectedArchivePoem(null) // Clear selected archive poem when switching to new poem tab
      setIllustrationUrl(null)
      setIsGeneratingImage(false)
    }
  }

  const handlePromptKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      // Only submit if not loading and prompt is not empty
      if (!isLoading && prompt.trim()) {
        (e.target as HTMLTextAreaElement).form?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      }
    }
  };

  const renderNewPoemTab = () => (
    <form
      className="prompt-form"
      onSubmit={handleSubmit}
    >
      <textarea
        className="prompt-textarea"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handlePromptKeyDown}
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
      <div className="mode-toggle">
        <label className="mode-checkbox">
          <input
            type="checkbox"
            checked={is80sMode}
            onChange={(e) => setIs80sMode(e.target.checked)}
          />
          <span className="mode-label">1980s Mode</span>
        </label>
      </div>
    </form>
  )

  const renderArchiveTab = () => (
    <div className="archive-container">
      <div className="archive-list">
        {archivePoems.length === 0 ? (
          <div className="archive-loading">
            <p>Loading archive poems...</p>
            <p>Count: {archivePoems.length}</p>
          </div>
        ) : (
          archivePoems.map((archivePoem) => (
            <div
              key={archivePoem.id}
              className="archive-poem-item"
              onClick={() => handleArchivePoemClick(archivePoem)}
            >
              <div className="archive-poem-title">{archivePoem.title}</div>
              <div className="archive-poem-id">#{archivePoem.id}</div>
            </div>
          ))
        )}
      </div>
    </div>
  )

  return (
    <div className="layout">
      {/* Left column: fixed width, always visible */}
      <div className={`left-column${activeTab === 'archive' ? ' archive-active' : ''}`}>
        <div className="tab-container">
          <div className={`tab-header${activeTab === 'archive' ? ' archive-active' : ''}`}>
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
          <div className={`tab-content${activeTab === 'archive' ? ' archive-active' : ''}`}>
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
                {/* Render generate image button or generated image */}
                {poem && !illustrationUrl && !isGeneratingImage && (
                  <div className="poem-image-container">
                    <button 
                      className="generate-image-button"
                      onClick={startImageGeneration}
                      disabled={isGeneratingImage}
                    >
                      Generate Image
                    </button>
                  </div>
                )}
                
                {/* Show loading state when generating */}
                {isGeneratingImage && (
                  <div className="poem-image-container">
                    <div className="image-generating">
                      <img src="/images/ui/loader.gif" alt="Generating..." className="loading-gif" />
                      <span>Generating Image...</span>
                    </div>
                  </div>
                )}
                
                {/* Show generated image when ready */}
                {illustrationUrl && (
                  <div className="poem-image-container">
                    <img 
                      src={illustrationUrl}
                      alt={`Generated illustration for ${poem.title}`}
                      className="poem-image"
                      onError={(e) => {
                        // Hide the image if it fails to load
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  </div>
                )}
              </>
                      ) : selectedArchivePoem ? (
            <>
              <div className="poem-title">{selectedArchivePoem.title}</div>
              <div className="poem-body">{selectedArchivePoem.content}</div>
              {selectedArchivePoem.signature && <div className="poem-signature">{selectedArchivePoem.signature}</div>}
              {/* Render image if it exists for this poem */}
              <div className="poem-image-container">
                <img 
                  src={`/images/${selectedArchivePoem.id}.png`}
                  alt={`Illustration for ${selectedArchivePoem.title}`}
                  className="poem-image"
                  onError={(e) => {
                    // Hide the image if it doesn't exist
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
            </>

            ) : isLoading ? (
              <div className="loading">
                <img src="/images/ui/loader.gif" alt="Loading..." className="loading-gif" />
                <span>Generating your poem...</span>
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