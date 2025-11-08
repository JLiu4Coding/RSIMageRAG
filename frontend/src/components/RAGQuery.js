import React, { useState } from 'react';
import { ragQuery, getImageSrcUrl } from '../api/client';

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
    <div>
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
          style={{ width: '100%' }}
        >
          {querying ? '💭 Processing...' : '💬 Ask Question'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div style={{ marginTop: '25px' }}>
          <h3 style={{ marginBottom: '15px', color: '#2d3748' }}>Answer</h3>
          <div style={{ 
            padding: '20px', 
            backgroundColor: 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%)',
            backgroundColor: '#e0f2fe',
            borderRadius: '12px',
            borderLeft: '4px solid #0ea5e9',
            marginBottom: '20px'
          }}>
            <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8', color: '#0c4a6e' }}>
              {result.answer}
            </p>
          </div>

          {result.sources && result.sources.length > 0 && (
            <div style={{ marginTop: '25px' }}>
              <h3 style={{ marginBottom: '15px', color: '#2d3748' }}>
                Sources ({result.sources.length})
              </h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
                gap: '15px'
              }}>
                {result.sources.map((source, idx) => (
                  <div 
                    key={idx} 
                    style={{ 
                      padding: '15px',
                      backgroundColor: '#f7fafc',
                      borderRadius: '10px',
                      border: '1px solid #e2e8f0',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#edf2f7';
                      e.currentTarget.style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#f7fafc';
                      e.currentTarget.style.transform = 'translateY(0)';
                    }}
                  >
                    <p style={{ fontWeight: '600', marginBottom: '10px', color: '#2d3748' }}>
                      Source {idx + 1}
                    </p>
                    {source.s3_url && (
                      <div style={{ marginBottom: '10px' }}>
                        <img 
                          src={getImageSrcUrl(source.s3_url, source.image_id || '')}
                          alt={`Source ${idx + 1}`}
                          style={{
                            width: '100%',
                            height: '120px',
                            objectFit: 'contain',
                            borderRadius: '6px',
                            backgroundColor: '#edf2f7'
                          }}
                        />
                      </div>
                    )}
                    {source.snippet && (
                      <p style={{ fontSize: '13px', color: '#4a5568', lineHeight: '1.6' }}>
                        {source.snippet}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default RAGQuery;

