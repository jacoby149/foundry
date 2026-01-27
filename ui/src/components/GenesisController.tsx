import React, { useEffect, useRef, useState, useCallback } from 'react';
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
  
  // 1. DEFAULT TO PHYSICS MODE (False)
  const [isTestMode, setIsTestMode] = useState<boolean>(false);
  
  // Stream Key forces the <img> to reload when connection drops
  const [streamKey, setStreamKey] = useState(Date.now()); 

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // --- DYNAMIC ENDPOINTS ---
  const prefix = isTestMode ? "stream" : "sim_stream";
  const STREAM_URL = `http://${backendUrl}/${prefix}/video_feed?t=${streamKey}`;
  const WS_URL = `ws://${backendUrl}/${prefix}/ws`;

  // --- ROBUST WEBSOCKET CONNECTION ---
  useEffect(() => {
    // Clear any pending reconnects if URL changes
    if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);

    const connect = () => {
      console.log(`[WS] Connecting to: ${WS_URL}`);
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[WS] Connected");
        setIsConnected(true);
        // When WS connects, force image refresh too (syncs them up)
        setStreamKey(Date.now());
      };

      ws.onclose = () => {
        console.log("[WS] Disconnected. Retrying in 2s...");
        setIsConnected(false);
        // 2. AUTO RECONNECT LOGIC
        reconnectTimeoutRef.current = setTimeout(connect, 2000);
      };

      ws.onerror = (err) => {
        console.warn("[WS] Error:", err);
        ws.close(); // Trigger onclose to handle retry
      };
    };

    connect();

    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
    };
  }, [WS_URL]); 

  // --- ROBUST STREAM HANDLING ---
  const handleStreamError = () => {
      // 3. AUTO HEAL VIDEO STREAM
      // If image fails to load, wait 1s and try again
      if (isConnected) {
          // If WS is connected but image failed, retry fast
          setTimeout(() => setStreamKey(Date.now()), 1000);
      } else {
          // If WS is down, retry slower
          setTimeout(() => setStreamKey(Date.now()), 3000);
      }
  };

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
      setStreamKey(Date.now()); 
  };

  return (
    <div className="genesis-wrapper">
      <div className="genesis-header">
        <div className="header-left">
            <h2>{isTestMode ? "Simple Stream Test" : "MuJoCo Physics"}</h2>
            <div className={`status-badge ${isConnected ? 'live' : 'offline'}`}>
            <span className="dot">●</span> 
            {isConnected ? "CONNECTED" : "RECONNECTING..."}
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
        {/* 4. LOADING OVERLAY */}
        {!isConnected && (
            <div className="stream-overlay">
                <div className="spinner"></div>
                <p>Waiting for Engine...</p>
            </div>
        )}
        
        <img 
            key={streamKey} 
            src={STREAM_URL} 
            alt="Simulation Feed" 
            className="video-feed"
            onError={handleStreamError} // Self-healing logic
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
