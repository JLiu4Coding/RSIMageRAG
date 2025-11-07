# ImageRAG Frontend

React frontend for remote sensing image analysis with RAG and agentic capabilities.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure API URL (optional):
```bash
cp .env.example .env
# Edit .env if backend is on different URL
```

3. Run the development server:
```bash
npm start
```

The app will open at http://localhost:3000

## Features

- **Upload Images**: Upload remote sensing images (GeoTIFF, JPEG, PNG)
- **Search Images**: Natural language search for images
- **RAG Query**: Ask questions answered using image captions
- **Agent Analysis**: Autonomous analysis with AI agent and tools

## Build

To build for production:
```bash
npm run build
```

