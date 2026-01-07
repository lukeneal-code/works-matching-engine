import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Music } from 'lucide-react';
import Upload from './components/Upload';
import BatchList from './components/BatchList';
import BatchDetails from './components/BatchDetails';

function Header() {
  const location = useLocation();

  return (
    <header className="header">
      <div className="container">
        <h1>
          <Music size={24} />
          Works Matching Engine
        </h1>
        <nav>
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
            Upload
          </Link>
          <Link to="/batches" className={location.pathname.startsWith('/batches') ? 'active' : ''}>
            Batches
          </Link>
        </nav>
      </div>
    </header>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div>
        <Header />
        <main className="container" style={{ paddingTop: '32px', paddingBottom: '48px' }}>
          <Routes>
            <Route path="/" element={<Upload />} />
            <Route path="/batches" element={<BatchList />} />
            <Route path="/batches/:batchId" element={<BatchDetails />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
