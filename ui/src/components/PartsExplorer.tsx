import { useMemo, useState } from "react";

const mockParts = Array.from({ length: 21 }, (_, i) => ({
  id: i + 1,
  name: `Part ${String.fromCharCode(65 + i)}`,
  image: `https://placehold.co/240x160?text=Part+${i + 1}`,
  tags: [(i % 2 ? "left" : "right"), (i % 3 ? "steel" : "plastic")],
}));

export default function PartsExplorer() {
  const [query, setQuery] = useState("");
  const [library, setLibrary] = useState<typeof mockParts>([]);
  const [showLibrary, setShowLibrary] = useState(false);

  const filtered = useMemo(
    () =>
      mockParts.filter(
        (p) =>
          p.name.toLowerCase().includes(query.trim().toLowerCase()) ||
          p.tags.some((tag) =>
            tag.toLowerCase().includes(query.trim().toLowerCase())
          )
      ),
    [query]
  );

  function addToLibrary(part: typeof mockParts[0]) {
    if (!library.some((p) => p.id === part.id)) setLibrary(l => [...l, part]);
  }

  function removeFromLibrary(part: typeof mockParts[0]) {
    setLibrary(l => l.filter(p => p.id !== part.id));
  }

  return (
    <div style={{textAlign:"center"}}>
      <h1 style={{
        fontWeight: 700,
        fontSize: 38,
        margin: "0 0 34px 0",
        letterSpacing:"-0.02em"
      }}>Parts Explorer</h1>
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        margin: "0 auto 32px auto",
        gap: 16
      }}>
        <input
          type="text"
          placeholder="Start typing to search parts by name or tag…"
          autoFocus
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            width: 480,
            height: 52,
            padding: "0 22px",
            fontSize: 19,
            borderRadius: 16,
            border: "2px solid var(--border)",
            background: "var(--card-bg)",
            fontWeight: 500,
            boxShadow: "0 2px 16px rgba(100,120,200,0.04)",
            outline: "none",
            transition: "border 0.18s"
          }}
        />
        <button style={{
          fontSize:16,
          background:"var(--card-bg)",
          border:"1.5px solid var(--primary)",
          color:"var(--primary)",
          borderRadius:14,
          height:48,
          fontWeight:600,
          padding:"0 24px",
          cursor:"pointer"
        }} onClick={()=>setShowLibrary(s=>!s)}>
          {showLibrary ? 'Hide Library' : 'Show Library'}
          {library.length ? ` (${library.length})`:""}
        </button>
      </div>
      {showLibrary &&
        <div style={{
          background:"var(--card-bg)",
          border:"1px solid var(--border)",
          borderRadius: 16,
          padding:16,
          margin:"0 auto 38px auto",
          maxWidth:940,
          boxShadow:"var(--shadow)"
        }}>
          <h2 style={{fontWeight:600,fontSize:22,margin:"0 0 12px 0"}}>Parts Library</h2>
          {library.length === 0 ? <p style={{color:"var(--text-light)"}}>No parts in your library yet.</p> : (
            <div style={{display:"flex",gap:26,flexWrap:"wrap",justifyContent:"center"}}>
              {library.map(part => (
                <div key={part.id} style={{
                  background:"#2222",
                  border:"1px solid var(--border)",
                  borderRadius:10,
                  padding:10,
                  minWidth:122
                }}>
                  <div style={{fontWeight:600}}>{part.name}</div>
                  <button style={{
                    border:"none",
                    background:"none",
                    color:"var(--primary)",
                    cursor:"pointer",
                    marginTop:3
                  }} onClick={()=>removeFromLibrary(part)}>Remove</button>
                </div>
              ))}
            </div>
          )}
        </div>
      }
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(240px,1fr))",gap:32,maxWidth:1100,margin:"0 auto"}}>
        {filtered.length === 0 && <p>No parts found.</p>}
        {filtered.map((part) => (
          <div
            key={part.id}
            style={{
              border: "1px solid var(--border)",
              borderRadius: 16,
              background: "var(--card-bg)",
              padding: 14,
              boxShadow: "0 2px 8px rgba(10,10,80,0.03)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              transition:'box-shadow 0.18s',
            }}
          >
            <img
              src={part.image}
              alt={part.name}
              style={{
                width: "100%",
                height: 120,
                objectFit: "cover",
                borderRadius: 8,
                marginBottom: 10,
                background:"#eaeaea"
              }}
            />
            <strong style={{fontSize:17,margin: "0 0 7px 0"}}>{part.name}</strong>
            <div style={{ marginTop: 4,display:"flex",gap:6 }}>
              {part.tags.map((tag) => (
                <span
                  key={tag}
                  style={{
                    fontSize: 13,
                    background: "#f3f6fc",
                    borderRadius: 8,
                    padding: "2px 10px",
                    color:"#5870a3",
                    fontWeight:500
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
            {!library.some(p=>p.id===part.id) ? (
              <button style={{
                marginTop:12,
                background:"var(--primary)",
                color:"#fff",
                border:"none",
                padding:"7px 18px",
                borderRadius:8,
                cursor:"pointer",
                fontWeight:600
              }} onClick={()=>addToLibrary(part)}>Add to Library</button>
            ):(
              <button disabled style={{
                marginTop:12,
                background:"var(--card-bg)",
                color:"var(--primary-dark)",
                border:"1px solid var(--primary-dark)",
                padding:"7px 18px",
                borderRadius:8,
                fontWeight:600,
                opacity:.55
              }}>In Library</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
