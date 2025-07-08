import { Link } from 'react-router-dom';

export type Poem = {
  id: string;
  title: string;
};

interface PoemListProps {
  poems: Poem[];
  selectedPoemId?: string;
  onPoemClick?: (id: string) => void;
}

const PoemList = ({ poems, selectedPoemId, onPoemClick }: PoemListProps) => {
  return (
    <div className="archive-container">
      <div className="archive-list">
        {poems.length === 0 ? (
          <div className="loading">
            <img src="/loader.gif" alt="Loading..." className="loading-gif" />
            <span>Loading poems...</span>
          </div>
        ) : (
          poems.map((poem) => (
            <Link
              key={poem.id}
              to={`/poem/${poem.id}`}
              className={`archive-poem-item${selectedPoemId === poem.id ? ' selected' : ''}`}
              onClick={() => onPoemClick && onPoemClick(poem.id)}
            >
              <div className="archive-poem-title">{poem.title}</div>
              <div className="archive-poem-id">#{poem.id}</div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
};

export default PoemList; 