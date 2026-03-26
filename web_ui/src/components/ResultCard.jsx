import { ShieldCheck, TriangleAlert } from "lucide-react";

export default function ResultCard({ result }) {
  if (!result) return null;

  const isFake = result.verdict === "fake";
  const confidencePercent = (result.confidence * 100).toFixed(1);

  return (
    <div className={`result-card ${isFake ? "fake" : "real"}`}>
      <div className="result-header">
        <div className="result-icon-container">
          {isFake ? (
             <TriangleAlert size={32} />
          ) : (
             <ShieldCheck size={32} />
          )}
        </div>
        <h2 className="result-title">
          {isFake ? "Synthetic Media Detected" : "Authentic Media Confirmed"}
        </h2>
      </div>
      
      <div className="stat-grid">
        <div className="stat-item">
          <span className="stat-label">Confidence</span>
          <span className="stat-value">{confidencePercent}%</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Inference Time</span>
          <span className="stat-value">{result.inference_time.toFixed(3)}s</span>
        </div>
      </div>

      <div className="confidence-section">
        <div className="confidence-header">
          <span className="stat-label">Detection Certainty</span>
          <span className="stat-label" style={{ color: isFake ? 'var(--fake-color)' : 'var(--real-color)' }}>
            {confidencePercent}%
          </span>
        </div>
        <div className="confidence-bar-bg">
          <div 
            className="confidence-bar-fill"
            style={{ width: `${Math.max(5, result.confidence * 100)}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
