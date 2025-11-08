import React from 'react';
import './App.css';
import ImageUpload from './components/ImageUpload';
import ImageSearch from './components/ImageSearch';
import RAGQuery from './components/RAGQuery';
import AgentQuery from './components/AgentQuery';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>🌍 ImageRAG</h1>
          <p className="subtitle">Remote Sensing Image Analysis Platform</p>
        </div>
      </header>

      <main className="main-container">
        <div className="sections-grid">
          {/* Image Upload Section */}
          <section className="section-card upload-section">
            <div className="section-header">
              <h2>📤 Upload & Analyze Images</h2>
              <p className="section-description">Upload remote sensing images and get AI-powered analysis</p>
            </div>
            <ImageUpload />
          </section>

          {/* Image Search Section */}
          <section className="section-card search-section">
            <div className="section-header">
              <h2>🔍 Search Images</h2>
              <p className="section-description">Find images using natural language queries</p>
            </div>
            <ImageSearch />
          </section>

          {/* RAG Query Section */}
          <section className="section-card rag-section">
            <div className="section-header">
              <h2>💬 RAG Query</h2>
              <p className="section-description">Ask questions about your images using AI</p>
            </div>
            <RAGQuery />
          </section>

          {/* Agent Analysis Section */}
          <section className="section-card agent-section">
            <div className="section-header">
              <h2>🤖 Agentic Analysis</h2>
              <p className="section-description">Autonomous AI agent for complex image analysis tasks</p>
            </div>
            <AgentQuery />
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
