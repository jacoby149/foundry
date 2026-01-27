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
  
  // TOGGLE STATE: Default to Test Mode so you can check connection first
  const [isTestMode, setIsTestMode] = useState<boolean>(true);
  const [streamKey, setStreamKey] = useState(Date.now()); // Forces img reload

  const wsRef = useRef<WebSocket | null>(null);

  // --- DYNAMIC ENDPOINT SWITCHING ---
  // If Test Mode -> "/stream"
  // If Physics Mode -> "/sim_stream"
  const prefix = isTestMode ? "stream" : "sim_stream";
  
  // We add ?t=... to force the browser to drop the old connection and start a new one
  const STREAM_URL = `http://${backendUrl}/${prefix}/video_feed?t=${streamKey}`;
  const WS_URL = `ws://${backendUrl}/${prefix}/ws`;

  // --- WEBSOCKET CONNECTION ---
  useEffect(() => {
    console.log(`[Switching Network] Connecting to: ${WS_URL}`);
    
    // Close existing connection if any
    if (wsRef.current) wsRef.current.close();

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    ws.onerror = () => setIsConnected(false);

    return () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    };
  }, [WS_URL]); // Triggered when WS_URL changes (via toggle)

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
      setStreamKey(Date.now()); // This forces the <img> tag to refresh
  };

  return (
    <div className="genesis-wrapper">
      <div className="genesis-header">
        <div className="header-left">
            <h2>{isTestMode ? "Simple Stream Test" : "MuJoCo Physics"}</h2>
            <div className={`status-badge ${isConnected ? 'live' : 'offline'}`}>
            <span className="dot">●</span> 
            {isConnected ? "CONNECTED" : "DISCONNECTED"}
            </div>
        </div>
        
        <button 
            className={`mode-toggle ${isTestMode ? 'test-mode' : 'real-mode'}`}
            onClick={toggleMode}
        >
            {isTestMode ? "→ Switch to Physics Engine" : "← Switch to Test Mode"}
        </button>
      </div>

      <div className="stream-container">
        {/* key={streamKey} forces React to destroy and recreate this element when toggling */}
        <img 
            key={streamKey} 
            src={STREAM_URL} 
            alt="Simulation Feed" 
            className="video-feed" 
        />
      </div>

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
          <p>Current Backend: <code>/{prefix}</code></p>
          <p>{isTestMode ? "Testing Network Latency" : "Controlling Physics Engine"}</p>
        </div>
      </div>
    </div>
  );
};

export default GenesisController;
