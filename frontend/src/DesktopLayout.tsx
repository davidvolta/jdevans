import { Routes, Route, useLocation } from 'react-router-dom';
import PoemList from './PoemList';
import PromptForm from './PromptForm';
import type { Poem } from './PoemList';
import PoemView from './PoemView';

interface DesktopLayoutProps {
  poems: (Poem & { body: string })[];
}

const DesktopLayout = ({ poems }: DesktopLayoutProps) => {
  const location = useLocation();
  const match = location.pathname.match(/^\/poem\/(.+)$/);
  const selectedPoemId = match ? match[1] : undefined;

  const handlePromptSubmit = (prompt: string) => {
    // TODO: Implement poem generation
    console.log('Generating poem for prompt:', prompt);
  };

  return (
    <div className="layout">
      <div className="left-column">
        <PromptForm onSubmit={handlePromptSubmit} />
        <PoemList poems={poems} selectedPoemId={selectedPoemId} />
      </div>
      <div className="right-column">
        <Routes>
          <Route path="/" element={<div />} />
          <Route path="/poem/:id" element={<PoemView poems={poems} />} />
        </Routes>
      </div>
    </div>
  );
};

export default DesktopLayout; 