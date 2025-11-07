import React, { useState } from 'react';
import { ragQuery } from '../api/client';

function RAGQuery() {
  const [question, setQuestion] = useState('');
  const [querying, setQuerying] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleQuery = async () => {
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setQuerying(true);
    setError(null);

    try {
      const queryResult = await ragQuery(question, 4);
      setResult(queryResult);
    } catch (err) {
      setError(err.response?.data?.detail || 'Query failed');
    } finally {
      setQuerying(false);
    }
  };

  return (
    <div className="card">
      <h2>RAG Query</h2>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Ask questions about the uploaded images. The system will use image captions to answer.
      </p>

      <div style={{ marginBottom: '20px' }}>
        <textarea
          className="textarea"
          placeholder="e.g., 'What types of land cover are present in the images?', 'Which images show urban areas?'"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button
          className="button"
          onClick={handleQuery}
          disabled={querying}
        >
          {querying ? 'Processing...' : 'Ask Question'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div>
          <h3>Answer</h3>
          <div className="card" style={{ marginTop: '10px', backgroundColor: '#f8f9fa' }}>
            <p style={{ whiteSpace: 'pre-wrap' }}>{result.answer}</p>
          </div>

          {result.sources && result.sources.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3>Sources ({result.sources.length})</h3>
              {result.sources.map((source, idx) => (
                <div key={idx} className="card" style={{ marginBottom: '10px', marginTop: '10px' }}>
                  <p><strong>Source {idx + 1}</strong></p>
                  {source.s3_url && (
                    <p>
                      <a href={source.s3_url} target="_blank" rel="noopener noreferrer">
                        View Image
                      </a>
                    </p>
                  )}
                  {source.snippet && (
                    <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                      {source.snippet}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default RAGQuery;

