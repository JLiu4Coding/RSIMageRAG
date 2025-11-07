import React, { useState } from 'react';
import './App.css';
import ImageUpload from './components/ImageUpload';
import ImageSearch from './components/ImageSearch';
import RAGQuery from './components/RAGQuery';
import AgentQuery from './components/AgentQuery';

function App() {
  const [activeTab, setActiveTab] = useState('upload');

  return (
    <div className="App">
      <header className="App-header">
        <h1>ImageRAG - Remote Sensing Image Analysis</h1>
        <nav className="tabs">
          <button
            className={activeTab === 'upload' ? 'active' : ''}
            onClick={() => setActiveTab('upload')}
          >
            Upload Images
          </button>
          <button
            className={activeTab === 'search' ? 'active' : ''}
            onClick={() => setActiveTab('search')}
          >
            Search Images
          </button>
          <button
            className={activeTab === 'rag' ? 'active' : ''}
            onClick={() => setActiveTab('rag')}
          >
            RAG Query
          </button>
          <button
            className={activeTab === 'agent' ? 'active' : ''}
            onClick={() => setActiveTab('agent')}
          >
            Agent Analysis
          </button>
        </nav>
      </header>

      <main className="container">
        {activeTab === 'upload' && <ImageUpload />}
        {activeTab === 'search' && <ImageSearch />}
        {activeTab === 'rag' && <RAGQuery />}
        {activeTab === 'agent' && <AgentQuery />}
      </main>
    </div>
  );
}

export default App;

