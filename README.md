# J.D. Evans Poem Generator

A fullstack application that generates poems in the style of J.D. Evans using a RAG-lite approach with semantic similarity search.

## Project Structure

```
├── frontend/          # Next.js TypeScript frontend
├── backend/           # FastAPI Python backend
├── poem_parser.py     # Poem parsing utility
└── poems.json         # Parsed poem data
```

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+ and pip

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Enter a prompt in the text area (e.g., "fishing on a rainy day", "traffic jams", "coffee in the morning")
3. Click "Generate Poem" to create a poem in J.D. Evans style
4. The generated poem will appear below the form

## API Endpoints

- `POST /generate` - Generate a poem based on a prompt
- `GET /` - API root endpoint
- `GET /health` - Health check endpoint

## Current Features

- ✅ Frontend with Next.js and TypeScript
- ✅ Backend with FastAPI
- ✅ Semantic similarity search using TF-IDF and cosine similarity
- ✅ Mock poem generation (ready for OpenAI integration)
- ✅ CORS configuration for local development
- ✅ Error handling and loading states

## Next Steps

- [ ] Integrate OpenAI API for actual poem generation
- [ ] Add vector database for better embeddings
- [ ] Implement proper poem embedding using OpenAI's text-embedding-3-small
- [ ] Add more sophisticated prompt engineering
- [ ] Improve UI/UX design
- [ ] Add poem history and favorites 