import { useState, useEffect } from 'react';

interface PromptFormProps {
  onSubmit: (prompt: string) => void;
  isLoading?: boolean;
}

const PromptForm = ({ onSubmit, isLoading = false }: PromptFormProps) => {
  const [prompt, setPrompt] = useState('');
  const [showForm, setShowForm] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    onSubmit(prompt.trim());
    setPrompt('');
    setShowForm(false);
  };

  // Reset form when loading starts
  useEffect(() => {
    if (isLoading) {
      setShowForm(false);
      setPrompt('');
    }
  }, [isLoading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && prompt.trim()) {
        (e.target as HTMLTextAreaElement).form?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      }
    }
  };

  if (!showForm) {
    return (
      <button
        className="new-poem-button"
        onClick={() => setShowForm(true)}
        disabled={false}
      >
        New Poem
      </button>
    );
  }

  return (
    <form 
      className="prompt-form" 
      onSubmit={handleSubmit}
    >
      <textarea
        className="prompt-textarea"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={2}
        placeholder="What is your poem about"
        disabled={false}
        autoFocus
        ref={(el) => {
          if (el) {
            el.focus();
          }
        }}
      />
      <button
        type="submit"
        className="prompt-button show"
        disabled={!prompt.trim()}
      >
        Create
      </button>
    </form>
  );
};

export default PromptForm; 