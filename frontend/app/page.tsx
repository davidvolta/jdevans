'use client'

import { useState, useEffect } from 'react'

interface GenerateResponse {
  poem: string
  similar_poems: string[]
}

export default function Home() {
  const [prompt, setPrompt] = useState('')
  const [generatedPoem, setGeneratedPoem] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  // Default poem to show on page load
  const defaultPoem = `Tribute to a 'Subber Code'

For two weeks dow I'b had this code.
A subber code! It's bery bad.
A scratchy throat, a ruddy doze,
ed doebody seebs to udderstad
be wed I talk. I get doe sbiles or sybathy.
(A leper has bore freds thad be.)
By ears are stuvved, I hack ed wheeze,
I cough ed gasp, I sdiff ed sdeeze.
I'b purchased ebery rebedy
the drug stores sell - frob A to Z.
Aspirid. Codact. Sidu-tabs.
Bicks idhalers. Pills ed caps-
ules. Duthig works. Dot chicked soup,
or herbal tea; oradge juice or cadaloupe.

Ed writig poebs is tough edough,
but try it wed your doze is stuvved!
Duthig seebs to rhybe today,
ed there's just wud thig I wad to say:

Pobes are bade by fools like be.
Who write wed they're id bisery.

Aaaazcheeesh! Eduff. I quit this ode,
by "Tribute To A Subber Code."

(J.D. Evans, a pseudonym, is a South Jersey writer who can pronounce
the letters 'n' and 'm' ... occasionally.)`

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim()) return

    setIsLoading(true)
    setError('')
    setGeneratedPoem('')

    try {
      const response = await fetch('http://localhost:8000/generate', {
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
      setGeneratedPoem(data.poem)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="layout">
        <div className="left-column">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <textarea
                id="prompt"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isLoading}
              />
            </div>

            <button 
              type="submit" 
              className="button" 
              disabled={isLoading || !prompt.trim()}
            >
              {isLoading ? 'Generating...' : 'Write'}
            </button>
          </form>

          {error && (
            <div style={{ color: 'red', marginTop: '1rem' }}>
              Error: {error}
            </div>
          )}

          {isLoading && (
            <div className="loading">
              Generating your poem...
            </div>
          )}
        </div>

        <div className="right-column">
          <div className="poem-display">
            <pre>{generatedPoem || defaultPoem}</pre>
          </div>
        </div>
      </div>
    </div>
  )
} 