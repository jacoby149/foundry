import React, { useState, useRef, useEffect } from "react";

type Message = { role: "user" | "bot"; content: string };

function ChatIcon({ color = "currentColor" }: { color?: string }) {
  return (
    <svg width="18" height="18" viewBox="0 0 20 20" stroke="none" fill="none">
      <rect width="20" height="20" rx="4" fill="none" />
      <path
        d="M5 13v2.25c0 .4.42.65.75.47L9 14h6a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h0Z"
        stroke={color} strokeWidth={1.6} fill="none"
      />
      <circle cx="8" cy="10" r="1" fill={color} />
      <circle cx="12" cy="10" r="1" fill={color} />
    </svg>
  );
}
function ViewerIcon({ color = "currentColor" }: { color?: string }) {
  return (
    <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
      <rect width="20" height="20" rx="4" fill="none" />
      <rect x="4" y="6" width="12" height="8" rx="2.3" stroke={color} strokeWidth="1.6" />
      <circle cx="10" cy="10" r="2.5" stroke={color} strokeWidth="1.6" />
    </svg>
  );
}
function CopyIcon({ color = "currentColor" }: { color?: string }) {
  return (
    <svg width="17" height="17" viewBox="0 0 16 16" fill="none">
      <rect width="16" height="16" rx="2" fill="none" />
      <rect x="5" y="5" width="8" height="8" rx="1.5" stroke={color} strokeWidth="1.4" />
      <rect x="3" y="3" width="8" height="8" rx="1.5" stroke={color} strokeWidth="1.2" opacity=".6" />
    </svg>
  );
}

export default function PartsMakerChat() {
  const [panels, setPanels] = useState<{ chat: boolean; viewer: boolean }>({
    chat: true,
    viewer: true,
  });
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", content: "Hello! How can I help you with your part?" },
  ]);
  const [input, setInput] = useState("");
  const [viewerUrl, setViewerUrl] = useState(
    "https://ochafik.com/openscad2/#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"
  );
  const [justCopied, setJustCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  const pageSidePad = 32;
  const pageInnerPad = 24;
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, panels.chat]);

  function ensureAtLeastOne(panel: "chat" | "viewer") {
    if (panels.chat && panels.viewer) setPanels({ ...panels, [panel]: !panels[panel] });
    else { if (!panels[panel]) setPanels({ ...panels, [panel]: true }); }
  }

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    setLoading(true);

    try {
      const response = await fetch("/chat/ask_for_object", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_text: input })
      });
      if (!response.ok) {
        throw new Error("API error");
      }
      const data = await response.json();
      // Get reply text and encoded viewer url:
      const reply = data?.chat_response?.reply_text ?? "Bot error (missing reply_text)";
      const url = data?.encoded_url ?? viewerUrl;
      setMessages((prev) => [...prev, { role: "bot", content: reply }]);
      setViewerUrl(url);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "Sorry, there was an error fetching from the server." }
      ]);
    }
    setLoading(false);
    setInput("");
  }

  function copyViewerUrl() {
    navigator.clipboard.writeText(viewerUrl);
    setJustCopied(true);
    setTimeout(() => setJustCopied(false), 1400);
  }

  function PanelButton({ active, onClick, icon, label }: {
    active: boolean; onClick: () => void; icon: React.ReactElement<any>; label: string;
  }) {
    return (
      <button
        type="button"
        onClick={onClick}
        style={{
          background: active
            ? "var(--primary)"
            : "var(--card-bg)",
          color: active ? "#fff" : "var(--text)",
          border: active
            ? "1.5px solid var(--primary)"
            : "1.5px solid var(--border)",
          fontWeight: 600,
          fontSize: 16,
          borderRadius: 9,
          padding: "0 18px 0 12px",
          height: 42,
          display: "flex",
          alignItems: "center",
          gap: 9,
          lineHeight: 1,
          cursor: "pointer",
          outline: "none",
          boxShadow: active ? "0 2px 6px rgba(39, 93, 255,.09)" : "none",
          transition: "background .14s, color .14s, border .17s, box-shadow .14s",
          minWidth: 80,
          position: "relative",
        }}
        tabIndex={0}
        onFocus={e =>
          (e.currentTarget.style.boxShadow =
            "0 0 0 2.6px var(--primary), 0 2px 6px rgba(70,128,255,.08)")
        }
        onBlur={e =>
          (e.currentTarget.style.boxShadow = active
            ? "0 2px 6px rgba(39,93,255,.09)"
            : "none")
        }
      >
        <span aria-hidden style={{
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center"
        }}>
          {React.cloneElement(icon, { color: active ? "#fff" : "var(--primary)" })}
        </span>
        <span style={{
          fontWeight: 700,
          fontSize: "16px",
          color: active ? "#fff" : "var(--text)",
          position: "relative",
          top: 1
        }}>
          {label}
        </span>
      </button>
    );
  }

  const split = panels.chat && panels.viewer;

  return (
    <div
      style={{
        position: "fixed",
        inset: `64px 0 0 0`,
        background: "var(--bg)",
        display: "flex",
        flexDirection: "column",
        height: `calc(100vh - 64px)`,
        zIndex: 0,
        boxSizing: "border-box",
        padding: `${pageInnerPad}px ${pageSidePad}px`,
      }}
    >
      {/* Controls */}
      <div
        style={{
          width: "fit-content",
          margin: "12px auto 15px auto",
          display: "flex",
          gap: 10,
        }}
      >
        <PanelButton
          icon={<ChatIcon />}
          label="Chat"
          active={panels.chat}
          onClick={() => ensureAtLeastOne("chat")}
        />
        <PanelButton
          icon={<ViewerIcon />}
          label="Viewer"
          active={panels.viewer}
          onClick={() => ensureAtLeastOne("viewer")}
        />
      </div>

      {/* Main Panels */}
      <div
        style={{
          flex: 1,
          display: split ? "flex" : "block",
          alignItems: "stretch",
          minHeight: 0,
          width: "100%",
          transition: "all .17s cubic-bezier(.68,.1,.34,1.08)"
        }}
      >
        {panels.chat && (
          <div
            style={{
              flex: split ? "0 1 50%" : 1,
              minWidth: 240,
              background: "var(--card-bg)",
              borderRadius: "13px",
              margin: split ? "0 6px 0 0" : `0 auto`,
              boxShadow: "var(--shadow)",
              height: "100%",
              display: "flex",
              flexDirection: "column",
              overflow: "hidden",
              border: "1.5px solid var(--border)",
              transition: "all .2s cubic-bezier(.8,.2,.19,1.05)",
            }}
          >
            <div
              style={{
                flex: 1,
                overflowY: "auto",
                overflowX: "hidden",
                padding: "28px 24px 0 24px",
                scrollbarColor: "var(--border) var(--bg)",
                overscrollBehaviorY: "contain"
              }}
            >
              {messages.map((msg, i) => (
                <div key={i} style={{
                  display: "flex",
                  justifyContent:
                    msg.role === "user" ? "flex-end" : "flex-start",
                  width: "100%"
                }}>
                  <div style={{
                    background: msg.role === "user" ? "var(--primary)" : "var(--chat-assistant)",
                    color: msg.role === "user" ? "#fff" : "var(--text)",
                    borderRadius: 14,
                    padding: "12px 16px",
                    fontSize: 16,
                    maxWidth: 400,
                    margin: "0 0 10px 0",
                    boxShadow: msg.role === "user"
                      ? "0 2px 8px rgba(37,99,235,0.10)"
                      : "0 1px 7px rgba(130,150,200,0.04)",
                    transition: "background .13s"
                  }}>
                    {msg.content}
                    {loading && msg.role === "bot" && i === messages.length - 1 && (
                      <span style={{ marginLeft: 6 }}>
                        <span className="blink">…</span>
                      </span>
                    )}
                  </div>
                </div>
              ))}
              <div ref={chatRef} />
            </div>
            <form
              onSubmit={sendMessage}
              style={{
                marginTop: "auto",
                padding: "17px 14px 10px 14px",
                display: "flex",
                gap: 8,
                borderTop: "1.2px solid var(--border)",
                background: "var(--card-bg)",
              }}
            >
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Type your message…"
                autoFocus={panels.chat}
                style={{
                  flex: 1,
                  border: "1.5px solid var(--border)",
                  borderRadius: 7,
                  padding: "12px",
                  fontSize: 16,
                  background: "var(--card-bg)",
                  color: "var(--text)",
                  fontWeight: 500,
                  outline: "none",
                  transition: "border .13s"
                }}
                disabled={loading}
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                style={{
                  background: input.trim() && !loading ? "var(--primary)" : "var(--border)",
                  color: input.trim() && !loading ? "#fff" : "var(--text-light)",
                  borderRadius: 7,
                  fontWeight: 700,
                  border: "none",
                  fontSize: 16,
                  padding: "0 19px",
                  cursor: input.trim() && !loading ? "pointer" : "not-allowed",
                  transition: "background .13s"
                }}
              >
                {loading ? "Sending…" : "Send"}
              </button>
            </form>
          </div>
        )}

        {split && (
          <div
            style={{
              width: 0,
              minWidth: 0,
              borderLeft: "1.5px solid var(--border)",
              height: "100%",
              alignSelf: "stretch",
              margin: "0 6px"
            }}
            aria-hidden
          />
        )}

        {panels.viewer && (
          <div
            style={{
              flex: split ? "0 1 50%" : 1,
              minWidth: 240,
              background: "var(--card-bg)",
              height: "100%",
              boxShadow: "var(--shadow)",
              borderRadius: 13,
              margin: split ? "0 0 0 6px" : "0 auto",
              display: "flex",
              flexDirection: "column",
              alignItems: "stretch",
              overflow: "hidden",
              border: "1.5px solid var(--border)",
              transition: "all .16s cubic-bezier(.64,.02,.32,1.08)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                padding: "11px 9px 8px 16px",
                background: "var(--card-bg)",
                borderBottom: "1.2px solid var(--border)",
                gap: 6
              }}
            >
              <span style={{
                fontSize: 13.5,
                color: "var(--text-light)",
                marginRight: 5,
                fontWeight: 500
              }}>
                Viewer URL:
              </span>
              <input
                type="text"
                value={viewerUrl}
                spellCheck={false}
                onChange={e => setViewerUrl(e.target.value)}
                style={{
                  flex: 1,
                  fontFamily: "monospace",
                  fontSize: 15,
                  color: "var(--text)",
                  background: "var(--chat-assistant)",
                  border: "1px solid var(--border)",
                  borderRadius: 6,
                  padding: "4px 9px",
                  marginRight: 7,
                  transition: "background .12s, border .13s"
                }}
                readOnly
              />
              <button
                type="button"
                style={{
                  border: justCopied
                    ? "1.5px solid var(--primary)"
                    : "1.5px solid var(--border)",
                  background: justCopied
                    ? "var(--primary)"
                    : "var(--card-bg)",
                  color: justCopied ? "#fff" : "var(--primary)",
                  fontWeight: 600,
                  fontSize: 15,
                  borderRadius: 8,
                  height: 36,
                  minWidth: 44,
                  padding: "0 14px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transition: "background 0.14s, border .14s, color .14s",
                  cursor: "pointer",
                  boxShadow: justCopied ? "0 2px 10px var(--primary)" : "none",
                  gap: "7px",
                  outline: "none"
                }}
                onClick={copyViewerUrl}
                onFocus={e =>
                  (e.currentTarget.style.boxShadow = "0 0 0 2.6px var(--primary)")
                }
                onBlur={e =>
                  (e.currentTarget.style.boxShadow = justCopied ? "0 2px 10px var(--primary)" : "none")
                }
              >
                <CopyIcon color={justCopied ? "#fff" : "var(--primary)"} />
                <span style={{ fontWeight: 650 }}>
                  {justCopied ? "Copied!" : "Copy"}
                </span>
              </button>
            </div>
            <iframe
              title="3D Viewer"
              src={viewerUrl}
              style={{
                border: "none",
                width: "100%",
                height: "100%",
                flex: 1,
                background: "#fff"
              }}
              key={viewerUrl}
            />
          </div>
        )}
      </div>
      <style>
        {`
          .blink {
            animation: blinkAnim .9s steps(2, start) infinite;
          }
          @keyframes blinkAnim { to { opacity: 0; } }
        `}
      </style>
    </div>
  );
}
