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
  const wsRef = useRef<WebSocket | null>(null);

  // Construct URLs
  const STREAM_URL = `http://${backendUrl}/genesis_stream/video_feed`;
  const WS_URL = `ws://${backendUrl}/genesis_stream/ws`;

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    ws.onerror = () => setIsConnected(false);

    return () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    };
  }, [WS_URL]);

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

  return (
    <div className="genesis-wrapper">
      <div className="genesis-header">
        <h2>Genesis Robot Teleoperation</h2>
        <div className={`status-badge ${isConnected ? 'live' : 'offline'}`}>
          <span className="dot">●</span> 
          {isConnected ? "CONNECTED" : "DISCONNECTED"}
        </div>
      </div>

      <div className="stream-container">
        <img src={STREAM_URL} alt="Genesis Simulation" className="video-feed" />
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
          <p>Use <strong>Arrow Keys</strong> to move.</p>
        </div>
      </div>
    </div>
  );
};

export default GenesisController;
