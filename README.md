# ImageRAG - Full Stack Remote Sensing Image Analysis

A full-stack application for analyzing remote sensing images using vision language models, RAG, and agentic AI.

## Features

- **Image Upload & Storage**: Upload images to AWS S3 with metadata management
- **Vision Model Analysis**: Analyze images using GPT-4o vision model
- **Vector Search**: Semantic search for images using natural language queries
- **RAG System**: Question answering using image captions as context
- **Agentic Analysis**: Autonomous image analysis with AI agent and tools

## Project Structure

```
.
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   └── api/
│   └── package.json
└── README.md
```

## Quick Start

### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

Backend runs on http://localhost:8000

### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm start
```

Frontend runs on http://localhost:3000

## API Endpoints

- `POST /api/images/upload` - Upload image to S3
- `POST /api/images/analyze` - Analyze image with vision model
- `POST /api/images/search` - Search images by natural language
- `POST /api/rag/query` - Answer questions using RAG
- `POST /api/agent/query` - Agentic analysis with tools
- `GET /api/images/{image_id}/url` - Get presigned image URL

## Environment Variables

### Backend (.env)
- `OPENAI_API_KEY` - OpenAI API key
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_DEFAULT_REGION` - AWS region
- `AWS_S3_BUCKET` - S3 bucket name
- `LANGCHAIN_API_KEY` - LangChain API key (optional)

### Frontend (.env)
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)

## Usage

1. **Upload Images**: Use the Upload tab to upload remote sensing images
2. **Analyze**: Click "Analyze Image" to generate captions using vision model
3. **Search**: Use natural language to search for relevant images
4. **RAG Query**: Ask questions about uploaded images
5. **Agent Analysis**: Use AI agent to autonomously analyze images

## Example Queries

- Search: "urban areas with high building density"
- RAG: "What types of land cover are present in the images?"
- Agent: "Find all forest images and analyze their structure"

## Notes

- Images are stored in AWS S3
- Image captions are indexed in FAISS vector store
- Vision model uses GPT-4o for analysis
- Agent uses LangChain tools for autonomous operations

