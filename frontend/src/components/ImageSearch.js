import React, { useState } from 'react';
import { searchImages, getImageSrcUrl } from '../api/client';

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
    <div>
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
          style={{ width: '100%' }}
        >
          {searching ? '🔍 Searching...' : '🔍 Search Images'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {results && (
        <div style={{ marginTop: '25px' }}>
          <h3 style={{ marginBottom: '20px', color: '#2d3748' }}>
            Search Results ({results.length})
          </h3>
          {results.length === 0 ? (
            <div style={{ 
              padding: '30px', 
              textAlign: 'center', 
              color: '#718096',
              backgroundColor: '#f7fafc',
              borderRadius: '8px'
            }}>
              <p>No images found matching your query.</p>
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
              gap: '20px',
              marginTop: '20px'
            }}>
              {results.map((result, idx) => (
                <div 
                  key={idx} 
                  style={{ 
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    padding: '15px',
                    backgroundColor: 'white',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.boxShadow = '0 8px 16px rgba(0,0,0,0.12)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
                  }}
                >
                  {result.s3_url && (
                    <div style={{ 
                      width: '100%', 
                      height: '150px', 
                      marginBottom: '12px',
                      borderRadius: '8px',
                      overflow: 'hidden',
                      backgroundColor: '#f7fafc',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <img 
                        src={getImageSrcUrl(result.s3_url, result.image_id || '')}
                        alt={`Search result ${idx + 1}`}
                        style={{
                          maxWidth: '100%',
                          maxHeight: '100%',
                          objectFit: 'contain'
                        }}
                      />
                    </div>
                  )}
                  <p style={{ fontWeight: '600', marginBottom: '8px', color: '#2d3748' }}>
                    Result {idx + 1}
                  </p>
                  {result.snippet && (
                    <p style={{ fontSize: '13px', color: '#4a5568', lineHeight: '1.6', marginBottom: '8px' }}>
                      {result.snippet}
                    </p>
                  )}
                  {result.lat && result.lon && (
                    <p style={{ fontSize: '11px', color: '#718096', marginTop: '8px' }}>
                      📍 {result.lat.toFixed(4)}, {result.lon.toFixed(4)}
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

