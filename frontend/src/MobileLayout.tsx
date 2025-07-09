import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import PoemList from './PoemList';
import type { Poem } from './PoemList';
import PoemView from './PoemView';

interface MobileLayoutProps {
  poems: (Poem & { content: string; signature?: string })[];
  onPoemGenerated?: (newPoem: Poem & { content: string; signature?: string }) => void;
  onPoemUpdated?: (poemId: string, updatedPoem: Poem & { content: string; signature?: string }) => void;
  onPoemRemoved?: (poemId: string) => void;
}

const MobileLayout = ({ poems, onPoemGenerated, onPoemUpdated, onPoemRemoved }: MobileLayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatingPoemId, setGeneratingPoemId] = useState<string | null>(null);
  const match = location.pathname.match(/^\/poem\/(.+)$/);
  const selectedPoemId = match ? match[1] : undefined;

  const handlePromptSubmit = async (prompt: string) => {
    let nextIdStr: string = '';
    try {
      setIsGenerating(true);
      // Calculate next numeric ID
      const maxId = poems.length > 0 ? Math.max(...poems.map(p => Number(p.id))) : 0;
      const nextId = maxId + 1;
      nextIdStr = String(nextId);
      setGeneratingPoemId(nextIdStr);
      
      // Create a loading poem immediately
      const loadingPoem = {
        id: nextIdStr,
        title: 'Generating...',
        content: 'J.D. Evans is writing your poem...',
        signature: '',
      };
      
      // Add the loading poem to the list immediately
      if (onPoemGenerated) {
        onPoemGenerated(loadingPoem);
      }
      
      // Navigate to the new poem URL immediately
      navigate(`/poem/${nextIdStr}`);
      
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });
      if (!response.ok) {
        throw new Error('Failed to generate poem');
      }
      const data = await response.json();
      
      // Update the poem with the real data
      const realPoem = {
        id: nextIdStr,
        title: data.title,
        content: data.body,
        signature: data.signature,
      };
      
      // Replace the loading poem with the real one
      if (onPoemUpdated) {
        onPoemUpdated(nextIdStr, realPoem);
      }
      
    } catch (error) {
      console.error('Error generating poem:', error);
      // Remove the loading poem on error
      if (onPoemRemoved && nextIdStr) {
        onPoemRemoved(nextIdStr);
      }
      navigate('/');
    } finally {
      setIsGenerating(false);
      setGeneratingPoemId(null);
    }
  };

  return (
    <div className="mobile-layout">
      <Routes>
        <Route path="/" element={
          <div className="mobile-home">
            <PoemList 
              poems={poems} 
              selectedPoemId={selectedPoemId}
              onPoemGenerated={handlePromptSubmit}
              isGenerating={isGenerating}
            />
          </div>
        } />
        <Route path="/poem/:id" element={
          <PoemView 
            poems={poems} 
            isGenerating={isGenerating}
            generatingPoemId={generatingPoemId}
          />
        } />
      </Routes>
    </div>
  );
};

export default MobileLayout; 