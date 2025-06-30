'use client'

import { useState } from 'react'
import './globals.css'

interface GenerateResponse {
  title: string
  body: string
  signature: string
  similar_poems: string[]
}

export default function Home() {
  const [prompt, setPrompt] = useState('')
  const [poem, setPoem] = useState<GenerateResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim()) return
    setIsLoading(true)
    setError('')
    setPoem(null)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/generate`, {
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

  return (
    <div className="layout">
      {/* Left column: fixed width, always visible */}
      <div className="left-column">
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
            {isLoading ? 'Generating...' : 'Write'}
          </button>
        </form>

        {error && (
          <div className="error">
            Error: {error}
          </div>
        )}

        {isLoading && (
          <div className="loading">
            Generating your poem...
          </div>
        )}
      </div>
      {/* Right column: scrollable, margin to avoid overlap with fixed left */}
      <div className="right-column">
        <div className="poem-display">
          {poem ? (
            <>
              <div className="poem-title">{poem.title}</div>
              <div className="poem-body">{poem.body}</div>
              {poem.signature && <div className="poem-signature">{poem.signature}</div>}
            </>
          ) : (
            'Your poem will appear here.'
          )}
        </div>
      </div>
    </div>
  )
} 