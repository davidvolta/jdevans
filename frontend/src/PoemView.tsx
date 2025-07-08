import { useParams } from 'react-router-dom';
import type { Poem } from './PoemList';

interface PoemViewProps {
  poems: (Poem & { body: string })[];
}

const PoemView = ({ poems }: PoemViewProps) => {
  const { id } = useParams<{ id: string }>();
  const poem = poems.find((p) => p.id === id);

  if (!poem) {
    return (
      <div className="poem-display">
        <div className="error">Poem not found.</div>
      </div>
    );
  }

  return (
    <div className={`poem-display${poem.id ? ' has-top-image' : ''}`}>
      {poem.id && (
        <div className="poem-image-container">
          <img 
            src={`/${poem.id}.png`}
            alt={`Illustration for ${poem.title}`}
            className="poem-image"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
            }}
          />
        </div>
      )}
      <div className="poem-title">{poem.title}</div>
      <div className="poem-body">{poem.body}</div>
      <div className="poem-signature">— occasionally</div>
    </div>
  );
};

export default PoemView; 