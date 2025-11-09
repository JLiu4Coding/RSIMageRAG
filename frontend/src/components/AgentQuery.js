import React, { useState } from 'react';
import { agentQuery } from '../api/client';

function AgentQuery() {
  const [query, setQuery] = useState('');
  const [imageId, setImageId] = useState('');
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Extract image URLs from text
  const extractImageUrls = (text) => {
    if (!text) return [];
    
    // Match URLs that point to image files
    const urlRegex = /(https?:\/\/[^\s\)]+\.(png|jpg|jpeg|gif|tif|tiff)(\?[^\s\)]*)?)/gi;
    const matches = text.match(urlRegex) || [];
    
    // Filter to only include image URLs and remove duplicates
    const uniqueUrls = [...new Set(matches)];
    
    // Prefer PNG/JPG over TIF for display
    const displayableUrls = uniqueUrls.filter(url => 
      /\.(png|jpg|jpeg|gif)(\?|$)/i.test(url)
    );
    
    // If no displayable images, include TIFs as well (they might be converted)
    return displayableUrls.length > 0 ? displayableUrls : uniqueUrls;
  };

  // Parse result text and render with images
  const renderResultWithImages = (text) => {
    if (!text) return null;
    
    const imageUrls = extractImageUrls(text);
    
    // Split text by image URLs to create segments
    const parts = [];
    let lastIndex = 0;
    
    imageUrls.forEach((url, idx) => {
      const urlIndex = text.indexOf(url, lastIndex);
      if (urlIndex > lastIndex) {
        parts.push({
          type: 'text',
          content: text.substring(lastIndex, urlIndex)
        });
      }
      parts.push({
        type: 'image',
        url: url,
        index: idx
      });
      lastIndex = urlIndex + url.length;
    });
    
    // Add remaining text
    if (lastIndex < text.length) {
      parts.push({
        type: 'text',
        content: text.substring(lastIndex)
      });
    }
    
    // If no images found, just return the text
    if (imageUrls.length === 0) {
      return <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.8', color: '#065f46' }}>{text}</p>;
    }
    
    return (
      <div>
        {parts.map((part, idx) => {
          if (part.type === 'text') {
            return (
              <p 
                key={idx} 
                style={{ 
                  whiteSpace: 'pre-wrap', 
                  lineHeight: '1.8', 
                  color: '#065f46',
                  marginBottom: part.content.trim() ? '15px' : '0'
                }}
              >
                {part.content}
              </p>
            );
          } else {
            // Check if it's a preview PNG or other displayable image
            const isDisplayable = /\.(png|jpg|jpeg|gif)(\?|$)/i.test(part.url);
            
            if (isDisplayable) {
              return (
                <div key={idx} style={{ marginBottom: '20px', marginTop: '15px' }}>
                  <div style={{
                    padding: '15px',
                    backgroundColor: '#f0f9ff',
                    borderRadius: '8px',
                    border: '1px solid #bae6fd'
                  }}>
                    <p style={{ 
                      fontSize: '13px', 
                      color: '#0c4a6e', 
                      marginBottom: '10px',
                      fontWeight: '500'
                    }}>
                      📷 Preview Image {part.index + 1}
                    </p>
                    <img 
                      src={part.url}
                      alt={`Preview ${part.index + 1}`}
                      style={{
                        maxWidth: '100%',
                        height: 'auto',
                        borderRadius: '6px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                        backgroundColor: '#fff',
                        display: 'block'
                      }}
                      onError={(e) => {
                        console.error('Failed to load image:', part.url);
                        e.target.style.display = 'none';
                        const errorDiv = e.target.nextSibling;
                        if (errorDiv) errorDiv.style.display = 'block';
                      }}
                    />
                    <div style={{ 
                      display: 'none',
                      padding: '20px',
                      textAlign: 'center',
                      color: '#666',
                      fontSize: '13px',
                      backgroundColor: '#f7fafc',
                      borderRadius: '6px',
                      marginTop: '10px'
                    }}>
                      ⚠️ Image could not be loaded
                      <br />
                      <a 
                        href={part.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ color: '#667eea', textDecoration: 'underline' }}
                      >
                        Open in new tab
                      </a>
                    </div>
                    <a 
                      href={part.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-block',
                        marginTop: '10px',
                        fontSize: '12px',
                        color: '#667eea',
                        textDecoration: 'none'
                      }}
                    >
                      🔗 Open full size
                    </a>
                  </div>
                </div>
              );
            } else {
              // For TIF files, show download link
              return (
                <div key={idx} style={{ marginBottom: '15px', marginTop: '10px' }}>
                  <a 
                    href={part.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-block',
                      padding: '8px 16px',
                      backgroundColor: '#e0f2fe',
                      color: '#0c4a6e',
                      borderRadius: '6px',
                      textDecoration: 'none',
                      fontSize: '13px',
                      fontWeight: '500',
                      border: '1px solid #bae6fd'
                    }}
                  >
                    📥 Download GeoTIFF
                  </a>
                </div>
              );
            }
          }
        })}
      </div>
    );
  };

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
            {renderResultWithImages(result.result)}
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

