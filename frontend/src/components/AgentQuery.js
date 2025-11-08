import React, { useState } from 'react';
import { agentQuery } from '../api/client';

function AgentQuery() {
  const [query, setQuery] = useState('');
  const [imageId, setImageId] = useState('');
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleQuery = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      const queryResult = await agentQuery(query, imageId || null);
      setResult(queryResult);
    } catch (err) {
      setError(err.response?.data?.detail || 'Agent query failed');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          className="input"
          placeholder="Image ID (optional)"
          value={imageId}
          onChange={(e) => setImageId(e.target.value)}
        />
        <textarea
          className="textarea"
          placeholder="e.g., 'Find all urban images and analyze their structure', 'Search for forest images and compare their features'"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          className="button"
          onClick={handleQuery}
          disabled={processing}
          style={{ width: '100%' }}
        >
          {processing ? '🤖 Processing...' : '🤖 Run Agent Query'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div style={{ marginTop: '25px' }}>
          <h3 style={{ marginBottom: '15px', color: '#2d3748' }}>Result</h3>
          <div style={{ 
            padding: '20px', 
            backgroundColor: '#d1fae5',
            borderRadius: '12px',
            borderLeft: '4px solid #10b981',
            marginBottom: '20px'
          }}>
            <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8', color: '#065f46' }}>
              {result.result}
            </p>
          </div>

          {result.steps && result.steps.length > 0 && (
            <div style={{ marginTop: '25px' }}>
              <h3 style={{ marginBottom: '15px', color: '#2d3748' }}>Steps</h3>
              <ol style={{ 
                marginLeft: '20px',
                padding: '15px',
                backgroundColor: '#f7fafc',
                borderRadius: '8px',
                listStylePosition: 'inside'
              }}>
                {result.steps.map((step, idx) => (
                  <li key={idx} style={{ marginBottom: '8px', color: '#4a5568', lineHeight: '1.6' }}>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {result.tools_used && result.tools_used.length > 0 && (
            <div style={{ marginTop: '25px' }}>
              <h3 style={{ marginBottom: '15px', color: '#2d3748' }}>Tools Used</h3>
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '10px'
              }}>
                {result.tools_used.map((tool, idx) => (
                  <span 
                    key={idx}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#e0f2fe',
                      color: '#0c4a6e',
                      borderRadius: '20px',
                      fontSize: '13px',
                      fontWeight: '500',
                      border: '1px solid #bae6fd'
                    }}
                  >
                    🔧 {tool}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AgentQuery;

