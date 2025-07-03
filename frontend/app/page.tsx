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
  const [prompt, setPrompt] = useState('')
  const [poem, setPoem] = useState<GenerateResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [archivePoems, setArchivePoems] = useState<ArchivePoem[]>([])
  const [selectedArchivePoem, setSelectedArchivePoem] = useState<ArchivePoem | null>(null)
  const [illustrationUrl, setIllustrationUrl] = useState<string | null>(null)
  const [isGeneratingImage, setIsGeneratingImage] = useState(false)

  // Load archive poems on component mount
  const loadArchivePoems = async () => {
    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${apiBaseUrl}/poems`);
      if (response.ok) {
        const data = await response.json();
        setArchivePoems(data.poems || []);
      }
    } catch (err) {
      // fail silently
    }
  };

  useEffect(() => {
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
        setIsGeneratingImage(false);
        clearInterval(interval);
      }
    }, 3000);
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
    setPrompt('') // Clear the prompt after submission
    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${apiBaseUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim()
        }),
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data: GenerateResponse = await response.json()
      setPoem(data)
      // Reload archive to include the new poem
      await loadArchivePoems()
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
    setIllustrationUrl(null)
    setIsGeneratingImage(false)
  }

  const handlePromptKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && prompt.trim()) {
        (e.target as HTMLTextAreaElement).form?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      }
    }
  };

  const handlePromptFocus = () => {
    // Button will become active when user focuses on the textarea
  };

  return (
    <div className="layout">
      <div className="left-column">
        <form
          className="prompt-form"
          onSubmit={handleSubmit}
        >
          <textarea
            className="prompt-textarea"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handlePromptKeyDown}
            onFocus={handlePromptFocus}
            rows={2}
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
        <div className="archive-container" style={{marginTop: 32}}>
          <div className="archive-list">
            {archivePoems.length === 0 ? (
              <div className="archive-loading">
                <p>Loading archive poems...</p>
              </div>
            ) : (
              archivePoems.map((archivePoem) => (
                <div
                  key={archivePoem.id}
                  className={`archive-poem-item${selectedArchivePoem?.id === archivePoem.id ? ' selected' : ''}`}
                  onClick={() => handleArchivePoemClick(archivePoem)}
                >
                  <div className="archive-poem-title">{archivePoem.title}</div>
                  <div className="archive-poem-id">#{archivePoem.id}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
      <div className="right-column">
        {(poem || selectedArchivePoem || isLoading || error) && (
          <div className={`poem-display${(poem && illustrationUrl) || (selectedArchivePoem) ? ' has-top-image' : ''}`}>
            {poem ? (
              <>
                {illustrationUrl && (
                  <div className="poem-image-container">
                    <img 
                      src={illustrationUrl}
                      alt={`Generated illustration for ${poem.title}`}
                      className="poem-image"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  </div>
                )}
                <div className="poem-title">{poem.title}</div>
                <div className="poem-body">{poem.body}</div>
                {poem.signature && <div className="poem-signature">{poem.signature}</div>}
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
                {isGeneratingImage && (
                  <div className="poem-image-container">
                    <div className="image-generating">
                      <img src="/images/ui/loader.gif" alt="Generating..." className="loading-gif" />
                      <span>Generating Image...</span>
                    </div>
                  </div>
                )}
              </>
            ) : selectedArchivePoem ? (
              <>
                <div className="poem-image-container">
                  <img 
                    src={`/images/${selectedArchivePoem.id}.png`}
                    alt={`Illustration for ${selectedArchivePoem.title}`}
                    className="poem-image"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                </div>
                <div className="poem-title">{selectedArchivePoem.title}</div>
                <div className="poem-body">{selectedArchivePoem.content}</div>
                {selectedArchivePoem.signature && <div className="poem-signature">{selectedArchivePoem.signature}</div>}
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
    </div>
  )
} 