import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import PoemList from './PoemList';
import PromptForm from './PromptForm';
import type { Poem } from './PoemList';
import PoemView from './PoemView';

interface MobileLayoutProps {
  poems: (Poem & { content: string; signature?: string })[];
  onPoemGenerated?: (newPoem: Poem & { content: string; signature?: string }) => void;
}

const MobileLayout = ({ poems, onPoemGenerated }: MobileLayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatingPoemId, setGeneratingPoemId] = useState<string | null>(null);
  const match = location.pathname.match(/^\/poem\/(.+)$/);
  const selectedPoemId = match ? match[1] : undefined;

  const handlePromptSubmit = async (prompt: string) => {
    try {
      setIsGenerating(true);
      // Calculate next numeric ID
      const maxId = poems.length > 0 ? Math.max(...poems.map(p => Number(p.id))) : 0;
      const nextId = maxId + 1;
      setGeneratingPoemId(String(nextId));
      // Navigate to the new poem URL immediately
      navigate(`/poem/${nextId}`);
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
      const newPoem = {
        id: String(nextId),
        title: data.title,
        content: data.body,
        signature: data.signature,
      };
      if (onPoemGenerated) {
        onPoemGenerated(newPoem);
      }
      // No need to navigate again; already on the correct URL
    } catch (error) {
      console.error('Error generating poem:', error);
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