import React, { useState } from 'react';
import { searchImages } from '../api/client';

function ImageSearch() {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setSearching(true);
    setError(null);

    try {
      const searchResult = await searchImages(query, 4);
      setResults(searchResult.results);
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="card">
      <h2>Search Images</h2>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Search for images using natural language queries
      </p>

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          className="input"
          placeholder="e.g., 'urban areas with high density', 'forest regions', 'coastal cities'"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          className="button"
          onClick={handleSearch}
          disabled={searching}
        >
          {searching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {results && (
        <div>
          <h3>Search Results ({results.length})</h3>
          {results.length === 0 ? (
            <p>No images found matching your query.</p>
          ) : (
            <div style={{ marginTop: '20px' }}>
              {results.map((result, idx) => (
                <div key={idx} className="card" style={{ marginBottom: '15px' }}>
                  <p><strong>Image {idx + 1}</strong></p>
                  {result.s3_url && (
                    <p>
                      <a href={result.s3_url} target="_blank" rel="noopener noreferrer">
                        View Image
                      </a>
                    </p>
                  )}
                  {result.snippet && (
                    <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                      {result.snippet}
                    </p>
                  )}
                  {result.lat && result.lon && (
                    <p style={{ marginTop: '5px', fontSize: '12px', color: '#999' }}>
                      Location: {result.lat.toFixed(4)}, {result.lon.toFixed(4)}
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

export default ImageSearch;

