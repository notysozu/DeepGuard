import { useState } from "react";
import { Shield, LoaderCircle } from "lucide-react";
import Header from "./components/Header";
import APIKeyInput from "./components/APIKeyInput";
import UploadArea from "./components/UploadArea";
import ResultCard from "./components/ResultCard";
import BackgroundEffects from "./components/BackgroundEffects";
import { TriangleAlert } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [token, setToken] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please provide a media file to analyze.");
      return;
    }
    if (!token) {
      setError("Authorization token is required.");
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
      
      // Delay for UX purposes so the loader shows a bit
      setTimeout(() => setResult(data), 600);
    } catch (err) {
      setError(err.message);
    } finally {
      setTimeout(() => setLoading(false), 600);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setResult(null);
      setError("");
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError("");
    }
  };

  return (
    <div className="page-container">
      <BackgroundEffects />
      
      <Header />

      <section className="glass-panel">
        <form onSubmit={handleSubmit}>
          
          <APIKeyInput token={token} setToken={setToken} />

          <UploadArea 
            file={file}
            dragActive={dragActive}
            handleDrag={handleDrag}
            handleDrop={handleDrop}
            handleFileChange={handleFileChange}
          />

          <button type="submit" className={`btn-primary ${loading ? 'loading' : ''}`} disabled={loading}>
            {loading ? (
              <>
                <LoaderCircle className="spinner" />
                <span>Analyzing Media...</span>
              </>
            ) : (
              <>
                <Shield size={20} />
                <span>Analyze Authenticity</span>
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="alert-message">
            <TriangleAlert size={20} />
            {error}
          </div>
        )}

        <ResultCard result={result} />
      </section>
    </div>
  );
}
