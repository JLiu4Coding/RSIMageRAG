# ImageRAG Backend

Backend API for remote sensing image analysis with RAG and agentic capabilities.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Setup Script
```bash
python setup.py
```
This will:
- Create necessary directories (uploads, images_jpeg, vectorstore)
- Check if .env file exists
- Verify required packages are installed

### 3. Configure Environment Variables
Create a `.env` file in the backend directory:
```bash
# Copy example (if available)
cp .env.example .env

# Or create manually with these required variables:
OPENAI_API_KEY=your_openai_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket_name
AWS_DEFAULT_REGION=us-west-1

# Optional
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langchain_api_key
```

### 4. Run the Server
```bash
# Option 1: Using the run script
python run.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

### 5. Test the API
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## API Endpoints

- `POST /api/images/upload` - Upload image to S3
- `POST /api/images/analyze` - Analyze image with vision model
- `POST /api/images/search` - Search images by natural language
- `POST /api/rag/query` - Answer questions using RAG
- `POST /api/agent/query` - Agentic analysis with tools
- `GET /api/images/{image_id}/url` - Get presigned image URL

## Features

- Image upload and S3 storage
- Vision model analysis (GPT-4o)
- Vector store for image retrieval
- RAG-based question answering
- Agentic analysis with tools

