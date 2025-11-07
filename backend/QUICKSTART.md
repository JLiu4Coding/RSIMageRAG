# Quick Start Guide

## After Installing Requirements

### Step 1: Run Setup Check
```bash
python setup.py
```

This will verify everything is ready and create necessary directories.

### Step 2: Create .env File

Create a `.env` file in the `backend` directory with your API keys:

```env
OPENAI_API_KEY=sk-your-openai-key-here
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-bucket-name
AWS_DEFAULT_REGION=us-west-1
```

**Important**: Replace all placeholder values with your actual credentials!

### Step 3: Start the Backend Server

```bash
# Easy way
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 4: Test the API

1. **Open API Docs**: Visit http://localhost:8000/docs
2. **Test Root Endpoint**: Visit http://localhost:8000

### Step 5: (Optional) Start the Frontend

In a new terminal:
```bash
cd ../frontend
npm install
npm start
```

Frontend will run at http://localhost:3000

## Troubleshooting

### "Module not found" errors
- Make sure you're in the `backend` directory
- Verify all packages installed: `pip list`

### "Settings validation error"
- Check your `.env` file exists and has all required variables
- Make sure there are no extra spaces in the `.env` file

### "AWS credentials error"
- Verify your AWS credentials in `.env`
- Check that your S3 bucket exists and is accessible

### "OpenAI API error"
- Verify your OpenAI API key is correct
- Check you have API credits available

## Next Steps

1. Upload an image via the API or frontend
2. Analyze the image to generate captions
3. Search for images using natural language
4. Ask questions using the RAG endpoint
5. Try agentic analysis with tools

