import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route /* ,NavLink */ } from 'react-router-dom';
import PartsMakerChat from './components/PartsMakerChat';
// import PartsExplorer from './components/PartsExplorer';

const navBarStyle: React.CSSProperties = {
  height: 64,
  display: 'flex',
  alignItems: 'center',
  padding: '0 2rem',
  background: 'var(--card-bg)',
  borderBottom: '1px solid var(--border)',
  fontWeight: 600,
  fontSize: 20,
  justifyContent: 'space-between'
};

export default function App() {
  const [theme, setTheme] = useState(() =>
    typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light'
  );

  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    const stored = localStorage.getItem('theme');
    if (stored) setTheme(stored);
  }, []);

  return (
    <Router>
      <nav style={navBarStyle}>
        <span style={{ fontWeight: 700, letterSpacing: -1 }}>Parts Studio</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 28 }}>
          <a
            href="http://localhost:8000"
            style={{
              color: 'var(--primary)',
              fontWeight: 500,
              fontSize: 16,
              textDecoration: 'underline',
              marginRight: 24
            }}
          >
            &larr; Go Back Home
          </a>
          <button
            aria-label="Toggle dark mode"
            style={{
              marginLeft: 24,
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: 24,
              color: theme === 'dark' ? 'var(--primary)' : '#aaa'
            }}
            onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
          >{theme === 'dark' ? "🌙" : "☀️"}</button>
        </span>
      </nav>      
      <main style={{
        maxWidth: 1100,
        margin: '40px auto 0 auto',
        padding: '0 16px',
      }}>
        <Routes>
          <Route path="ui/" element={<PartsMakerChat />} />
          {/* <Route path="ui/explorer" element={<PartsExplorer />} /> */}
        </Routes>
      </main>
    </Router>
  );
}
