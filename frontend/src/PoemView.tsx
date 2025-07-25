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
  const [isGeneratingImage, setIsGeneratingImage] = useState<boolean>(false);
  const [isLoadingPoem, setIsLoadingPoem] = useState<boolean>(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  // Reset states when poem changes
  useEffect(() => {
    setImageError(false);
    setIsLoadingPoem(true);
    setImageUrl(null);
  }, [id]);

  // Clear loading state when poem is found
  useEffect(() => {
    if (poem) {
      setIsLoadingPoem(false);
    }
  }, [poem]);

  // Reset scroll position to top when component mounts or poem changes
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [id]);

  // Auto-poll for image when poem loads (only for new poems that might be generating)
  useEffect(() => {
    if (!poem?.id) return;
    
    const checkForImage = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || '';
        const response = await fetch(`${apiUrl}/illustration?poem_id=${poem.id}`);
        const data = await response.json();
        
        if (data.status === 'ready') {
          setIsGeneratingImage(false);
          setImageError(false);
          setImageUrl(data.illustration_url);
        } else if (data.status === 'pending') {
          setIsGeneratingImage(true);
          setImageUrl(null);
          setTimeout(checkForImage, 2000); // Poll every 2 seconds
        } else if (data.status === 'classic') {
          // Classic poems don't get images generated
          setIsGeneratingImage(false);
          setImageUrl(null);
        } else {
          // No image exists and none is being generated - this is fine for older poems
          setIsGeneratingImage(false);
          setImageUrl(null);
        }
      } catch (error) {
        setIsGeneratingImage(false);
      }
    };
    
    // Always check for image when poem loads
    checkForImage();
  }, [poem?.id]);

  // Show loading state if we're generating and this is the generating poem
  if (isGenerating && generatingPoemId === id) {
    return (
      <div className="poem-display">
        <div className="loading">
          <div className="spinner"></div>
          <span>J.D. Evans is writing...</span>
        </div>
      </div>
    );
  }

  // Show loading state when switching between poems
  if (isLoadingPoem) {
    return (
      <div className="poem-display">
        <div className="loading">
          <div className="spinner"></div>
          <span>Loading poem...</span>
        </div>
      </div>
    );
  }

  if (!poem && poems.length > 0) {
    return (
      <div className="poem-display">
        <div className="error">Poem not found.</div>
      </div>
    );
  }

  if (!poem) {
    // Still loading poems or invalid state, render nothing
    return null;
  }

  const handleBackClick = () => {
    window.history.back();
  };

  return (
    <div className={`poem-display${poem.id && imageUrl && !imageError ? ' has-top-image' : ''}`}>
      <div className="poem-strip-inner">
        {poem.id && imageUrl && !imageError && (
          <div className="poem-image-container">
            <img 
              src={`${import.meta.env.VITE_API_URL || ''}${imageUrl}`}
              alt={`Illustration for ${poem.title}`}
              className="poem-image"
              onError={() => setImageError(true)}
            />
          </div>
        )}
        
        {/* Show loading message if image is being generated (only for new poems) */}
        {isGeneratingImage && (
          <div className="generate-image-section">
            <div className="creating-image">
              <span>Creating image</span>
              <div className="dots">
                <span className="dot dot1">.</span>
                <span className="dot dot2">.</span>
                <span className="dot dot3">.</span>
              </div>
            </div>
          </div>
        )}
        
        <div className="poem-title">{poem.title}</div>
        <div className="poem-body">{poem.content}</div>
        {poem.signature && <div className="poem-signature">{poem.signature}</div>}
        
        <button className="new-poem-button back-button-mobile" onClick={handleBackClick} style={{ marginTop: '2em', maxWidth: '400px', display: 'none' }}>
          Back to Poems
        </button>
      </div>
    </div>
  );
};

export default PoemView;