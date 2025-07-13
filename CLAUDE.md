# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a J.D. Evans poem generator web application with a React/TypeScript frontend and Python FastAPI backend. The app generates AI-powered poems in the style of J.D. Evans (a fictional poet) using OpenAI GPT-4 and includes AI-generated illustrations using DALL-E.

## Architecture

**Frontend (React + TypeScript + Vite)**
- Located in `frontend/`
- Uses React Router for client-side routing
- Responsive design with separate mobile/desktop layouts (`MobileLayout.tsx`, `DesktopLayout.tsx`)
- Main components: `PoemList.tsx`, `PoemView.tsx`, `PromptForm.tsx`
- Built with Vite, serves from port 5173 in dev

**Backend (Python FastAPI)**
- Located in `backend/`
- Serves both API endpoints and static React build files
- Uses OpenAI API for poem generation and embeddings
- Stores poems in `poems.json` with vector embeddings in `poems_with_embeddings.json`
- Generates and caches AI illustrations using DALL-E
- Images saved to `backend/static/images/`

**Key Data Flow:**
1. User submits prompt via frontend form
2. Backend finds similar poems using vector embeddings (cosine similarity)
3. GPT-4 generates new poem in J.D. Evans style using similar poems as examples
4. Background task generates illustration via DALL-E
5. Poem saved to `poems.json`, illustration cached and saved locally

## Development Commands

**Frontend (run from `frontend/` directory):**
```bash
npm install          # Install dependencies
npm run dev          # Start dev server (port 5173)
npm run build        # Build for production
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

**Backend (run from `backend/` directory):**
```bash
# IMPORTANT: Always use the venv's Python 3.8, NOT system Python 2.7
./venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000    # Start FastAPI server
```

**Full Build Process:**
```bash
./render-build.sh    # Complete build: resets poems, builds frontend, copies to backend/static
```

## Environment Setup

- Backend requires OpenAI API key and Stability API key in `.env` file
- Frontend uses `VITE_API_URL` environment variable for API endpoint
- **CRITICAL**: System has Python 2.7 default, but venv contains Python 3.8. Always use `./venv/bin/python` directly, never `python` or `source venv/bin/activate`

## Key Files

- `backend/main.py` - Main FastAPI application with all API endpoints
- `backend/poems.json` - User-generated poems storage
- `backend/poems_with_embeddings.json` - Sample poems with vector embeddings for similarity matching
- `frontend/src/App.tsx` - Main React app with responsive layout switching
- `render-build.sh` - Production build script

## Poetry Generation System

The core poetry generation uses a sophisticated similarity-based approach:
1. User prompts are embedded using OpenAI's text-embedding-3-small
2. Cosine similarity finds the 3 most similar poems from the sample collection
3. GPT-4-turbo generates new poems using these similar poems as style examples
4. All poems include the signature J.D. Evans biographical line format

## Quick Commands

**Git Push:** When user says `push "commit message"`, run:
```bash
./push.sh "commit message"
```