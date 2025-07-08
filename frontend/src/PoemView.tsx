import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import type { Poem } from './PoemList';

interface PoemViewProps {
  poems: (Poem & { content: string; signature?: string })[];
  isGenerating?: boolean;
  generatingPoemId?: string | null;
}

const PoemView = ({ poems, isGenerating = false, generatingPoemId = null }: PoemViewProps) => {
  const { id } = useParams<{ id: string }>();
  const poem = poems.find((p) => String(p.id) === id);
  const [imageError, setImageError] = useState<boolean>(false);

  // Reset image error state when poem changes
  useEffect(() => {
    setImageError(false);
  }, [id]);

  // Show loading state if we're generating and this is the generating poem
  if (isGenerating && generatingPoemId === id) {
    return (
      <div className="poem-display">
        <div className="loading">
          <div className="spinner"></div>
          <span>Generating poem...</span>
        </div>
      </div>
    );
  }

  if (!poem) {
    return (
      <div className="poem-display">
        <div className="error">Poem not found.</div>
      </div>
    );
  }

  return (
    <div className={`poem-display${poem.id && !imageError ? ' has-top-image' : ''}`}>
      {poem.id && !imageError && (
        <div className="poem-image-container">
          <img 
            src={`${import.meta.env.VITE_API_URL || ''}/static/${poem.id}.png`}
            alt={`Illustration for ${poem.title}`}
            className="poem-image"
            onError={() => {
              setImageError(true);
            }}
          />
        </div>
      )}
      <div className="poem-title">{poem.title}</div>
      <div className="poem-body">{poem.content}</div>
      {poem.signature && <div className="poem-signature">{poem.signature}</div>}
    </div>
  );
};

export default PoemView; 