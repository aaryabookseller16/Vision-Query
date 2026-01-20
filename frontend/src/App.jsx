import { useState } from "react";

/**
 * App.jsx
 *
 * Minimal VisionQuery UI:
 * - user types a text query
 * - we call the backend /search endpoint
 * - we display the ranked results
 *
 * Design goals:
 * - keep it dead simple and readable
 * - no fancy state management
 * - easy to extend later (image upload, ingest, etc.)
 */

const API_BASE = "/api";

async function ingestImage(path) {
  const res = await fetch(`${API_BASE}/ingest/image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
  return res.json();
}

async function search(query, top_k) {
  const res = await fetch(`${API_BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k }),
  });
  return res.json();
}

export default function App() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(e) {
    e.preventDefault();
    setError("");
    setResults([]);

    if (!query.trim()) {
      setError("Type a query first.");
      return;
    }

    try {
      setLoading(true);

      // Call backend search helper (uses fetch under the hood)
      const data = await search(query.trim(), Number(topK));

      if (data.error) {
        setError(data.error);
        return;
      }

      setResults(data.results ?? []);
    } catch (err) {
      setError(err?.message || "Something went wrong calling the API.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: 16 }}>
      <h1 style={{ marginBottom: 6 }}>VisionQuery</h1>
      <p style={{ marginTop: 0, opacity: 0.8 }}>
        Text-to-image search (MVP)
      </p>

      <form onSubmit={handleSearch} style={{ display: "flex", gap: 12 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='Try: "a red car"'
          style={{
            flex: 1,
            padding: 10,
            borderRadius: 8,
            border: "1px solid #ccc",
          }}
        />

        <input
          type="number"
          min={1}
          max={20}
          value={topK}
          onChange={(e) => setTopK(e.target.value)}
          style={{
            width: 90,
            padding: 10,
            borderRadius: 8,
            border: "1px solid #ccc",
          }}
          title="How many results to return"
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "10px 14px",
            borderRadius: 8,
            border: "1px solid #333",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && (
        <div style={{ marginTop: 12, color: "crimson" }}>
          {error}
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        <h3 style={{ marginBottom: 10 }}>Results</h3>

        {results.length === 0 && !loading && !error && (
          <div style={{ opacity: 0.7 }}>
            No results yet. Ingest an image, then search.
          </div>
        )}

        <ul style={{ paddingLeft: 18 }}>
          {results.map((r, idx) => (
            <li key={`${r.path}-${idx}`} style={{ marginBottom: 10 }}>
              <div>
                <strong>Path:</strong> <code>{r.path}</code>
              </div>
              <div>
                <strong>Score:</strong>{" "}
                {typeof r.score === "number" ? r.score.toFixed(4) : r.score}
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div style={{ marginTop: 24, opacity: 0.7, fontSize: 12 }}>
        Backend expected at <code>{API_BASE}</code>
      </div>
    </div>
  );
}