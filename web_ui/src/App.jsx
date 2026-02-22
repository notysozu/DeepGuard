import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [token, setToken] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Select a media file first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Prediction request failed");
      }
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <section className="card">
        <h1>DeepGuard</h1>
        <p>Binary authenticity detection for media files.</p>

        <form onSubmit={handleSubmit} className="form">
          <label>
            JWT Token
            <input
              type="text"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Paste bearer token"
            />
          </label>

          <label>
            Upload Media
            <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Analyzing..." : "Detect"}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className={`result ${result.verdict === "fake" ? "fake" : "real"}`}>
            <h2>
              {result.verdict === "fake"
                ? "Confirmed Synthetic Media"
                : "Authentic Media"}
            </h2>
            <p>Confidence: {(result.confidence * 100).toFixed(2)}%</p>
            <p>Model count: {result.model_count}</p>
            <p>Inference time: {result.inference_time}s</p>
          </div>
        )}
      </section>
    </main>
  );
}
