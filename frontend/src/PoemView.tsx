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
  const [imageGenerationError, setImageGenerationError] = useState<string | null>(null);

  // Reset image error state when poem changes
  useEffect(() => {
    setImageError(false);
    setImageGenerationError(null);
  }, [id]);

  // Reset scroll position to top when component mounts or poem changes
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [id]);

  const handleGenerateImage = async () => {
    if (!poem || isGeneratingImage) return;
    
    setIsGeneratingImage(true);
    setImageGenerationError(null);
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiUrl}/regenerate-illustration/${poem.id}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to start image generation');
      }
      
      // Poll for completion
      const pollForCompletion = async () => {
        const checkResponse = await fetch(`${apiUrl}/illustration?poem_id=${poem.id}`);
        const checkData = await checkResponse.json();
        
        if (checkData.status === 'ready') {
          setIsGeneratingImage(false);
          setImageError(false);
          // Force a re-render by updating the image src
          window.location.reload();
        } else if (checkData.status === 'pending') {
          setTimeout(pollForCompletion, 2000); // Poll every 2 seconds
        } else {
          throw new Error('Image generation failed');
        }
      };
      
      setTimeout(pollForCompletion, 2000); // Start polling after 2 seconds
      
    } catch (error) {
      setIsGeneratingImage(false);
      setImageGenerationError(error instanceof Error ? error.message : 'Failed to generate image');
    }
  };

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

  return (
    <div className={`poem-display${poem.id && !imageError ? ' has-top-image' : ''}`}>
      <div className="poem-strip-inner">
        {poem.id && !imageError && (
          <div className="poem-image-container">
            <img 
              src={`${import.meta.env.VITE_API_URL || ''}/static/images/${poem.id}.png`}
              alt={`Illustration for ${poem.title}`}
              className="poem-image"
              onError={() => setImageError(true)}
            />
          </div>
        )}
        
        {/* Show generate image button if no image or image failed to load */}
        {(!poem.id || imageError) && (
          <div className="generate-image-section">
            {imageGenerationError && (
              <div className="error" style={{ marginBottom: '1em' }}>
                {imageGenerationError}
              </div>
            )}
            <button
              className="generate-image-button"
              onClick={handleGenerateImage}
              disabled={isGeneratingImage}
            >
              {isGeneratingImage ? (
                <>
                  <div className="spinner" style={{ width: '16px', height: '16px', marginRight: '8px' }}></div>
                  Adding Image...
                </>
              ) : (
                'Add Image'
              )}
            </button>
          </div>
        )}
        
        <div className="poem-title">{poem.title}</div>
        <div className="poem-body">{poem.content}</div>
        {poem.signature && <div className="poem-signature">{poem.signature}</div>}
      </div>
    </div>
  );
};

export default PoemView;