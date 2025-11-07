import React, { useState } from 'react';
import { uploadImage, analyzeImage } from '../api/client';

function ImageUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const uploadResult = await uploadImage(file);
      setResult({
        type: 'upload',
        data: uploadResult,
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!result || !result.data?.image_id) {
      setError('Please upload an image first');
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      const analysisResult = await analyzeImage(result.data.image_id);
      setResult({
        ...result,
        type: 'analysis',
        analysis: analysisResult,
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="card">
      <h2>Upload and Analyze Images</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <input
          type="file"
          accept=".tif,.tiff,.jpg,.jpeg,.png"
          onChange={handleFileChange}
          style={{ marginBottom: '10px' }}
        />
        <button
          className="button"
          onClick={handleUpload}
          disabled={uploading || !file}
        >
          {uploading ? 'Uploading...' : 'Upload Image'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result?.type === 'upload' && (
        <div className="success">
          <p>Image uploaded successfully!</p>
          <p><strong>Image ID:</strong> {result.data.image_id}</p>
          <p><strong>S3 URL:</strong> <a href={result.data.s3_url} target="_blank" rel="noopener noreferrer">View Image</a></p>
          <button
            className="button"
            onClick={handleAnalyze}
            disabled={analyzing}
            style={{ marginTop: '10px' }}
          >
            {analyzing ? 'Analyzing...' : 'Analyze Image'}
          </button>
        </div>
      )}

      {result?.type === 'analysis' && result.analysis && (
        <div style={{ marginTop: '20px' }}>
          <h3>Analysis Results</h3>
          <div style={{ marginTop: '10px' }}>
            <p><strong>Location:</strong> {result.analysis.location_guess || 'Unknown'}</p>
            <p><strong>Land Cover:</strong> {result.analysis.land_cover || 'N/A'}</p>
            <p><strong>Urban Structure:</strong> {result.analysis.urban_structure || 'N/A'}</p>
            <p><strong>Notable Features:</strong> {result.analysis.notable_features || 'N/A'}</p>
            <p><strong>Summary:</strong> {result.analysis.summary || 'N/A'}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default ImageUpload;

