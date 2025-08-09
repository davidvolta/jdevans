import { Link } from 'react-router-dom';
import PromptForm from './PromptForm';

export type Poem = {
  id: string;
  title: string;
  type?: 'classic' | 'modern';
  image_filename?: string;
  newsItem?: string | null;
};

interface PoemListProps {
  poems: Poem[];
  selectedPoemId?: string;
  onPoemClick?: (id: string) => void;
  onPoemGenerated?: (prompt: string) => void;
  isGenerating?: boolean;
  activeTab?: 'classic' | 'new';
  onTabChange?: (tab: 'classic' | 'new') => void;
}

const PoemList = ({ poems, selectedPoemId, onPoemClick, onPoemGenerated, isGenerating, activeTab = 'classic', onTabChange }: PoemListProps) => {

  // Filter poems by type
  const classicPoems = poems.filter(poem => poem.type === 'classic');
  const newPoems = poems.filter(poem => poem.type === 'modern');

  // Wrapper function to handle prompt submission
  const handlePromptSubmit = (prompt: string) => {
    if (onPoemGenerated) {
      onPoemGenerated(prompt);
    }
  };

  const renderPoemList = (poemList: Poem[]) => (
    <div className="archive-list">
      {poemList.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
          No poems yet
        </div>
      ) : (
        poemList.map((poem) => (
          <Link
            key={String(poem.id)}
            to={`/poem/${poem.id}`}
            className={`archive-poem-item${String(selectedPoemId) === String(poem.id) ? ' selected' : ''}`}
            onClick={() => onPoemClick && onPoemClick(String(poem.id))}
          >
            <div className="archive-poem-id">#{poem.id}</div>
            <div className="archive-poem-title">{poem.title}</div>
          </Link>
        ))
      )}
    </div>
  );

  return (
    <div className="archive-container">
      {/* Title */}
      <div className="poems-title">
        J.D. Evans Poems
      </div>
      
      {/* Tab Navigation */}
      <div className="tab-navigation">
        <div
          className={`tab-button ${activeTab === 'classic' ? 'active' : ''}`}
          onClick={() => onTabChange && onTabChange('classic')}
        >
          CLASSIC
        </div>
        <div
          className={`tab-button ${activeTab === 'new' ? 'active' : ''}`}
          onClick={() => onTabChange && onTabChange('new')}
        >
          MODERN
        </div>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'classic' ? (
          renderPoemList(classicPoems)
        ) : (
          <div className="new-tab-content">
            <PromptForm onSubmit={handlePromptSubmit} isLoading={isGenerating} />
            <div style={{ marginTop: '24px' }}>
              {renderPoemList(newPoems)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PoemList; 