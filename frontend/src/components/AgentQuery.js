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
    <div className="card">
      <h2>Agentic Analysis</h2>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Use an AI agent with tools to autonomously analyze images. The agent can search, analyze, and process images automatically.
      </p>

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
        >
          {processing ? 'Processing...' : 'Run Agent Query'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div>
          <h3>Result</h3>
          <div className="card" style={{ marginTop: '10px', backgroundColor: '#f8f9fa' }}>
            <p style={{ whiteSpace: 'pre-wrap' }}>{result.result}</p>
          </div>

          {result.steps && result.steps.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3>Steps</h3>
              <ol style={{ marginLeft: '20px' }}>
                {result.steps.map((step, idx) => (
                  <li key={idx} style={{ marginBottom: '5px' }}>{step}</li>
                ))}
              </ol>
            </div>
          )}

          {result.tools_used && result.tools_used.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3>Tools Used</h3>
              <ul style={{ marginLeft: '20px' }}>
                {result.tools_used.map((tool, idx) => (
                  <li key={idx}>{tool}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AgentQuery;

