import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import PartsMakerChat from './components/PartsMakerChat';
import GenesisController from './components/GenesisController';
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

const linkStyle = ({ isActive }: { isActive: boolean }) => ({
  color: isActive ? 'var(--primary)' : 'inherit',
  textDecoration: 'none',
  marginRight: 20,
  fontSize: 16,
  opacity: isActive ? 1 : 0.7
});

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

  return (
    <Router>
      <nav style={navBarStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 30 }}>
            <span style={{ fontWeight: 700, letterSpacing: -1 }}>Parts Studio</span>
            
            {/* Added Navigation Links here */}
            <div style={{ marginLeft: 20, display: 'flex', alignItems: 'center' }}>
                <NavLink to="ui/" end style={linkStyle}>
                    Maker Chat
                </NavLink>
                <NavLink to="ui/play" style={linkStyle}>
                    Robot Play
                </NavLink>
            </div>
        </div>

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
        paddingBottom: '40px'
      }}>
        <Routes>
          <Route path="ui/" element={<PartsMakerChat />} />
          <Route path="ui/play" element={<GenesisController backendUrl="localhost:8000" />} />
          {/* <Route path="ui/explorer" element={<PartsExplorer />} /> */}
        </Routes>
      </main>
    </Router>
  );
}
