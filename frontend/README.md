# Frontend - J.D. Evans Poem Generator

Next.js TypeScript frontend for the J.D. Evans Poem Generator.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
app/
├── layout.tsx      # Root layout component
├── page.tsx        # Home page with poem generation form
└── globals.css     # Global styles
```

## Features

- ✅ TypeScript support
- ✅ Responsive design
- ✅ Form validation
- ✅ Loading states
- ✅ Error handling
- ✅ CORS configuration for backend communication

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`:

- `POST /generate` - Submit prompt and receive generated poem 