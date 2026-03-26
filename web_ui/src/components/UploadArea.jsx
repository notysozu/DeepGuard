import { CloudUpload, Image as ImageIcon } from "lucide-react";

export default function UploadArea({ 
  file, 
  dragActive, 
  handleDrag, 
  handleDrop, 
  handleFileChange 
}) {
  return (
    <div className="form-group" style={{ marginTop: '2rem' }}>
      <label className="form-label">
        <ImageIcon size={18} /> Upload Media to Analyze
      </label>
      <div 
        className={`upload-zone ${dragActive ? "drag-active" : ""}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input 
          type="file" 
          onChange={handleFileChange} 
          accept="image/*,video/*"
        />
        <CloudUpload className="upload-icon" />
        {file ? (
          <span className="file-name-pill">{file.name}</span>
        ) : (
          <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
            Drag & drop or <span style={{ color: 'var(--neon-blue)' }}>click to browse</span>
          </span>
        )}
      </div>
    </div>
  );
}
