import { useState } from 'react';

interface PromptFormProps {
  onSubmit: (prompt: string) => void;
  isLoading?: boolean;
}

const PromptForm = ({ onSubmit, isLoading = false }: PromptFormProps) => {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    onSubmit(prompt.trim());
    setPrompt('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && prompt.trim()) {
        (e.target as HTMLTextAreaElement).form?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
      }
    }
  };

  return (
    <form className="prompt-form" onSubmit={handleSubmit}>
      <textarea
        className="prompt-textarea"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={2}
        placeholder="Enter your prompt..."
        disabled={isLoading}
      />
      <button
        type="submit"
        className="prompt-button"
        disabled={isLoading || !prompt.trim()}
      >
        Write
      </button>
    </form>
  );
};

export default PromptForm; 