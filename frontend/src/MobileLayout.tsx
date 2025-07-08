import { Routes, Route, useNavigate } from 'react-router-dom';
import PoemList from './PoemList';
import PoemView from './PoemView';
import PromptForm from './PromptForm';
import type { Poem } from './PoemList';

interface MobileLayoutProps {
  poems: (Poem & { content: string; signature?: string })[];
}

const MobileLayout = ({ poems }: MobileLayoutProps) => {
  const navigate = useNavigate();

  const handlePromptSubmit = (prompt: string) => {
    // TODO: Implement poem generation
    console.log('Generating poem for prompt:', prompt);
  };

  return (
    <div className="layout">
      <Routes>
        <Route path="/" element={
          <div className="left-column">
            <PromptForm onSubmit={handlePromptSubmit} />
            <PoemList poems={poems} />
          </div>
        } />
        <Route
          path="/poem/:id"
          element={
            <div className="right-column">
              <button
                className="prompt-button"
                style={{ marginBottom: '1rem', maxWidth: '100px' }}
                onClick={() => navigate(-1)}
              >
                ← Back
              </button>
              <PoemView poems={poems} />
            </div>
          }
        />
      </Routes>
    </div>
  );
};

export default MobileLayout; 