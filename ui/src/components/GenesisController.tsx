import React, { useEffect, useRef, useState } from 'react';
import './GenesisController.css';

interface GenesisControllerProps {
  backendUrl?: string;
}

type KeyState = Record<string, boolean>;

const GenesisController: React.FC<GenesisControllerProps> = ({ 
  backendUrl = "localhost:8000" 
}) => {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [activeKeys, setActiveKeys] = useState<KeyState>({});
  
  // TOGGLE STATE: Default to Test Mode (Green Box)
  const [isTestMode, setIsTestMode] = useState<boolean>(true);
  
  // This helps force the browser to reload the image when we switch modes
  const [streamKey, setStreamKey] = useState(Date.now());

  const wsRef = useRef<WebSocket | null>(null);

  // --- DYNAMIC URLS ---
  const endpointPrefix = isTestMode ? "stream" : "genesis_stream";
  
  // We add ?t=... to force the browser to re-request the stream
  const STREAM_URL = `http://${backendUrl}/${endpointPrefix}/video_feed?t=${streamKey}`;
  const WS_URL = `ws://${backendUrl}/${endpointPrefix}/ws`;

  // --- WEBSOCKET CONNECTION ---
  useEffect(() => {
    console.log(`Connecting to: ${WS_URL}`);
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    ws.onerror = () => setIsConnected(false);

    return () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    };
  }, [WS_URL]); // Re-run this effect when WS_URL changes

  // --- KEYBOARD CONTROLS ---
  useEffect(() => {
    const validKeys = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"];

    const handleKeyEvent = (e: KeyboardEvent, type: 'down' | 'up') => {
      if (validKeys.includes(e.code)) {
        e.preventDefault();
        
        setActiveKeys((prev) => ({ ...prev, [e.code]: type === 'down' }));

        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            if (type === 'down' && e.repeat) return;
            const payload = JSON.stringify({ key: e.code, type: type });
            wsRef.current.send(payload);
        }
      }
    };

    const onKeyDown = (e: KeyboardEvent) => handleKeyEvent(e, "down");
    const onKeyUp = (e: KeyboardEvent) => handleKeyEvent(e, "up");

    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);

    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
    };
  }, []);

  const getKeyClass = (key: string) => {
    return activeKeys[key] ? "key-btn active" : "key-btn";
  };

  const toggleMode = () => {
      setIsTestMode(!isTestMode);
      setStreamKey(Date.now()); // Force video reload
  };

  return (
    <div className="genesis-wrapper">
      <div className="genesis-header">
        <div className="header-left">
            <h2>{isTestMode ? "Test Stream (Green Box)" : "Genesis Simulation"}</h2>
            <div className={`status-badge ${isConnected ? 'live' : 'offline'}`}>
            <span className="dot">●</span> 
            {isConnected ? "CONNECTED" : "DISCONNECTED"}
            </div>
        </div>
        
        <button 
            className={`mode-toggle ${isTestMode ? 'test-mode' : 'real-mode'}`}
            onClick={toggleMode}
        >
            {isTestMode ? "Switch to Real Physics" : "Switch to Test Mode"}
        </button>
      </div>

      <div className="stream-container">
        {/* We use key={streamKey} to force React to destroy and recreate the img tag */}
        <img 
            key={streamKey} 
            src={STREAM_URL} 
            alt="Simulation Feed" 
            className="video-feed" 
        />
      </div>

      {/* Control Pad */}
      <div className="control-panel">
        <div className="d-pad">
          <div className="d-row">
            <div className={getKeyClass("ArrowUp")}>▲</div>
          </div>
          <div className="d-row">
            <div className={getKeyClass("ArrowLeft")}>◀</div>
            <div className={getKeyClass("ArrowDown")}>▼</div>
            <div className={getKeyClass("ArrowRight")}>▶</div>
          </div>
        </div>
        <div className="instructions">
          <p>Mode: <strong>{isTestMode ? "SIMPLE TEST" : "PHYSICS ENGINE"}</strong></p>
          <p>Use <strong>Arrow Keys</strong> to move.</p>
        </div>
      </div>
    </div>
  );
};

export default GenesisController;
