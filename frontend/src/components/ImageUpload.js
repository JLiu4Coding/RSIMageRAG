import React, { useState } from 'react';
import { uploadImage, uploadMultipleImages, analyzeImage, getImageSrcUrl } from '../api/client';

function ImageUpload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState({}); // Track analyzing state per image
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [uploadMode, setUploadMode] = useState('single'); // 'single' or 'multiple'
  const [analysisResults, setAnalysisResults] = useState({}); // Store analysis results per image
  const [copiedId, setCopiedId] = useState(null); // Track which ID was copied

  const copyToClipboard = async (text, imageId) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(imageId);
      setTimeout(() => setCopiedId(null), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    if (uploadMode === 'single') {
      setFiles(selectedFiles.slice(0, 1));
    } else {
      setFiles(selectedFiles);
    }
    setResult(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      if (uploadMode === 'single' || files.length === 1) {
        // Single file upload
        const uploadResult = await uploadImage(files[0]);
        setResult({
          type: 'upload',
          data: uploadResult,
          mode: 'single'
        });
      } else {
        // Multiple file upload
        const uploadResult = await uploadMultipleImages(files);
        setResult({
          type: 'upload',
          data: uploadResult,
          mode: 'multiple'
        });
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (imageId) => {
    if (!imageId) {
      setError('Please provide an image ID');
      return;
    }

    setAnalyzing(prev => ({ ...prev, [imageId]: true }));
    setError(null);

    try {
      const analysisResult = await analyzeImage(imageId);
      setAnalysisResults(prev => ({
        ...prev,
        [imageId]: analysisResult
      }));
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setAnalyzing(prev => ({ ...prev, [imageId]: false }));
    }
  };

  return (
    <div>
      
      <div style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '10px' }}>
          <label style={{ marginRight: '15px' }}>
            <input
              type="radio"
              value="single"
              checked={uploadMode === 'single'}
              onChange={(e) => {
                setUploadMode(e.target.value);
                setFiles([]);
                setResult(null);
              }}
              style={{ marginRight: '5px' }}
            />
            Single Image
          </label>
          <label>
            <input
              type="radio"
              value="multiple"
              checked={uploadMode === 'multiple'}
              onChange={(e) => {
                setUploadMode(e.target.value);
                setFiles([]);
                setResult(null);
              }}
              style={{ marginRight: '5px' }}
            />
            Multiple Images
          </label>
        </div>
        
        <input
          type="file"
          accept=".tif,.tiff,.jpg,.jpeg,.png"
          onChange={handleFileChange}
          multiple={uploadMode === 'multiple'}
          style={{ marginBottom: '10px', display: 'block' }}
        />
        
        {files.length > 0 && (
          <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666' }}>
            {files.length} file{files.length > 1 ? 's' : ''} selected
          </div>
        )}
        
        <button
          className="button"
          onClick={handleUpload}
          disabled={uploading || files.length === 0}
        >
          {uploading ? 'Uploading...' : `Upload ${files.length > 1 ? `${files.length} Images` : 'Image'}`}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result?.type === 'upload' && result.mode === 'single' && (
        <div className="success" style={{ marginTop: '20px' }}>
          <h3>Uploaded Image</h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: '300px 1fr', 
            gap: '20px', 
            marginTop: '15px',
            alignItems: 'start'
          }}>
            <div>
              <img 
                src={getImageSrcUrl(result.data.s3_url, result.data.image_id)}
                alt={result.data.image_id}
                style={{
                  width: '100%',
                  height: 'auto',
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  objectFit: 'contain',
                  maxHeight: '300px',
                  backgroundColor: '#f8f9fa'
                }}
                onError={(e) => {
                  // Try backend fallback URL
                  const fallbackUrl = getImageSrcUrl(null, result.data.image_id);
                  if (e.target.src !== fallbackUrl && !e.target.src.includes('/api/images/')) {
                    e.target.src = fallbackUrl;
                  } else {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }
                }}
              />
              <div style={{ 
                display: 'none', 
                padding: '40px', 
                textAlign: 'center', 
                backgroundColor: '#f8f9fa', 
                borderRadius: '8px',
                color: '#666'
              }}>
                Image not available
              </div>
            </div>
            <div>
              <div style={{ marginBottom: '15px' }}>
                <p style={{ marginBottom: '8px' }}>
                  <strong>Image ID:</strong>
                </p>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '8px 12px',
                  backgroundColor: '#f8f9fa',
                  borderRadius: '6px',
                  border: '1px solid #e2e8f0'
                }}>
                  <code style={{
                    flex: 1,
                    fontFamily: 'monospace',
                    fontSize: '13px',
                    color: '#2d3748',
                    wordBreak: 'break-all',
                    userSelect: 'all',
                    cursor: 'text'
                  }}>
                    {result.data.image_id}
                  </code>
                  <button
                    onClick={() => copyToClipboard(result.data.image_id, result.data.image_id)}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: copiedId === result.data.image_id ? '#10b981' : '#667eea',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px',
                      fontWeight: '500',
                      transition: 'background-color 0.2s',
                      whiteSpace: 'nowrap'
                    }}
                    title="Copy Image ID"
                  >
                    {copiedId === result.data.image_id ? '✓ Copied' : '📋 Copy'}
                  </button>
                </div>
              </div>
              <p><strong>Status:</strong> <span style={{ color: '#155724' }}>✓ Uploaded</span></p>
              <button
                className="button"
                onClick={() => handleAnalyze(result.data.image_id)}
                disabled={analyzing[result.data.image_id]}
                style={{ marginTop: '15px' }}
              >
                {analyzing[result.data.image_id] ? 'Analyzing...' : 'Analyze Image'}
              </button>
            </div>
          </div>
          
          {/* Show analysis results inline */}
          {analysisResults[result.data.image_id] && (
            <div style={{ 
              marginTop: '20px', 
              padding: '15px', 
              backgroundColor: '#f8f9fa', 
              borderRadius: '8px',
              borderTop: '2px solid #007bff'
            }}>
              <h4 style={{ marginBottom: '10px', color: '#007bff' }}>Analysis Results</h4>
              <div style={{ 
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '15px'
              }}>
                <div>
                  <p><strong>Location:</strong> {analysisResults[result.data.image_id].location_guess || 'Unknown'}</p>
                  <p><strong>Land Cover:</strong> {analysisResults[result.data.image_id].land_cover || 'N/A'}</p>
                  <p><strong>Urban Structure:</strong> {analysisResults[result.data.image_id].urban_structure || 'N/A'}</p>
                  <p><strong>Notable Features:</strong> {analysisResults[result.data.image_id].notable_features || 'N/A'}</p>
                </div>
                <div style={{ 
                  padding: '10px', 
                  backgroundColor: '#e7f3ff', 
                  borderRadius: '4px' 
                }}>
                  <p><strong>Summary:</strong></p>
                  <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#004085' }}>
                    {analysisResults[result.data.image_id].summary || 'No summary available.'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {result?.type === 'upload' && result.mode === 'multiple' && (
        <div style={{ marginTop: '20px' }}>
          <div className="success" style={{ marginBottom: '20px' }}>
            <h3>Upload Results</h3>
            <p><strong>Total:</strong> {result.data.total} | 
               <strong style={{ color: '#155724', marginLeft: '10px' }}> Success:</strong> {result.data.success_count} | 
               <strong style={{ color: result.data.failed_count > 0 ? '#dc3545' : '#155724', marginLeft: '10px' }}> Failed:</strong> {result.data.failed_count}
            </p>
          </div>
          
          {result.data.uploaded.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3>Uploaded Images ({result.data.uploaded.length})</h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '20px',
                marginTop: '15px'
              }}>
                {result.data.uploaded.map((item, idx) => (
                  <div key={idx} style={{ 
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    padding: '15px',
                    backgroundColor: 'white',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    transition: 'transform 0.2s',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    <div style={{ 
                      width: '100%', 
                      height: '200px', 
                      marginBottom: '10px',
                      borderRadius: '4px',
                      overflow: 'hidden',
                      backgroundColor: '#f8f9fa',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative'
                    }}>
                      <img 
                        src={getImageSrcUrl(item.s3_url, item.image_id)}
                        alt={item.filename}
                        style={{
                          maxWidth: '100%',
                          maxHeight: '100%',
                          objectFit: 'contain'
                        }}
                        onError={(e) => {
                          // Try backend fallback URL
                          const fallbackUrl = getImageSrcUrl(null, item.image_id);
                          if (e.target.src !== fallbackUrl && !e.target.src.includes('/api/images/')) {
                            e.target.src = fallbackUrl;
                          } else {
                            e.target.style.display = 'none';
                            const errorDiv = e.target.nextSibling;
                            if (errorDiv) errorDiv.style.display = 'flex';
                          }
                        }}
                      />
                      <div style={{ 
                        display: 'none', 
                        padding: '20px', 
                        textAlign: 'center', 
                        color: '#666',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        position: 'absolute',
                        width: '100%',
                        height: '100%'
                      }}>
                        <span style={{ fontSize: '48px' }}>📷</span>
                        <span style={{ fontSize: '12px', marginTop: '10px' }}>Image not available</span>
                      </div>
                    </div>
                    <p style={{ 
                      fontWeight: 'bold', 
                      marginBottom: '8px',
                      fontSize: '14px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {item.filename}
                    </p>
                    <div style={{ marginBottom: '10px' }}>
                      <p style={{ fontSize: '11px', color: '#666', marginBottom: '5px' }}>
                        <strong>ID:</strong>
                      </p>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '6px 10px',
                        backgroundColor: '#f8f9fa',
                        borderRadius: '4px',
                        border: '1px solid #e2e8f0'
                      }}>
                        <code style={{
                          flex: 1,
                          fontFamily: 'monospace',
                          fontSize: '11px',
                          color: '#2d3748',
                          wordBreak: 'break-all',
                          userSelect: 'all',
                          cursor: 'text',
                          lineHeight: '1.4'
                        }}>
                          {item.image_id}
                        </code>
                        <button
                          onClick={() => copyToClipboard(item.image_id, item.image_id)}
                          style={{
                            padding: '4px 8px',
                            backgroundColor: copiedId === item.image_id ? '#10b981' : '#667eea',
                            color: 'white',
                            border: 'none',
                            borderRadius: '3px',
                            cursor: 'pointer',
                            fontSize: '10px',
                            fontWeight: '500',
                            transition: 'background-color 0.2s',
                            whiteSpace: 'nowrap',
                            flexShrink: 0
                          }}
                          title="Copy Image ID"
                        >
                          {copiedId === item.image_id ? '✓' : '📋'}
                        </button>
                      </div>
                    </div>
                    <button
                      className="button"
                      onClick={() => handleAnalyze(item.image_id)}
                      disabled={analyzing[item.image_id]}
                      style={{ 
                        width: '100%',
                        padding: '8px 12px', 
                        fontSize: '14px'
                      }}
                    >
                      {analyzing[item.image_id] ? 'Analyzing...' : 'Analyze'}
                    </button>
                    
                    {/* Show analysis results inline under each image */}
                    {analysisResults[item.image_id] && (
                      <div style={{ 
                        marginTop: '15px', 
                        padding: '12px', 
                        backgroundColor: '#f8f9fa', 
                        borderRadius: '6px',
                        borderLeft: '3px solid #007bff',
                        fontSize: '13px'
                      }}>
                        <div style={{ marginBottom: '8px' }}>
                          <strong>Location:</strong> {analysisResults[item.image_id].location_guess || 'Unknown'}
                        </div>
                        <div style={{ marginBottom: '8px' }}>
                          <strong>Land Cover:</strong> {analysisResults[item.image_id].land_cover || 'N/A'}
                        </div>
                        <div style={{ marginBottom: '8px' }}>
                          <strong>Summary:</strong> {analysisResults[item.image_id].summary || 'N/A'}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {result.data.failed.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3 style={{ color: '#dc3545' }}>Failed Uploads ({result.data.failed.length})</h3>
              <div style={{
                display: 'grid',
                gap: '10px',
                marginTop: '15px'
              }}>
                {result.data.failed.map((item, idx) => (
                  <div key={idx} style={{ 
                    padding: '15px', 
                    backgroundColor: '#f8d7da', 
                    borderRadius: '8px',
                    border: '1px solid #f5c6cb',
                    color: '#721c24'
                  }}>
                    <p style={{ fontWeight: 'bold', marginBottom: '5px' }}>{item.filename}</p>
                    <p style={{ fontSize: '13px' }}>Error: {item.error}</p>
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

export default ImageUpload;

