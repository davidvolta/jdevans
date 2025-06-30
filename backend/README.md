# Backend - J.D. Evans Poem Generator API

FastAPI Python backend for the J.D. Evans Poem Generator.

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

3. The API will be available at [http://localhost:8000](http://localhost:8000)

## API Documentation

Once the server is running, you can view the interactive API documentation at:
- [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)

## Available Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /generate` - Generate poem from prompt

## Request/Response Format

### Generate Poem

**Request:**
```json
{
  "prompt": "fishing on a rainy day"
}
```

**Response:**
```json
{
  "poem": "Generated poem text...",
  "similar_poems": ["similar poem 1", "similar poem 2"]
}
```

## Features

- ✅ FastAPI with automatic API documentation
- ✅ CORS middleware for frontend communication
- ✅ Semantic similarity search using TF-IDF
- ✅ Mock poem generation (ready for OpenAI integration)
- ✅ Error handling and validation
- ✅ Type hints and Pydantic models

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning (TF-IDF, cosine similarity)

## Next Steps

- [ ] Integrate OpenAI API for actual poem generation
- [ ] Add vector database for better embeddings
- [ ] Implement proper poem embedding using OpenAI's text-embedding-3-small
- [ ] Add more sophisticated prompt engineering 