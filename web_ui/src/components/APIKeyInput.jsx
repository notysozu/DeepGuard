import { Key } from "lucide-react";

export default function APIKeyInput({ token, setToken }) {
  return (
    <div className="form-group">
      <label className="form-label">
        <Key size={18} /> API Access Token
      </label>
      <input
        type="password"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        placeholder="Enter your bearer token..."
        className="input-field"
        autoComplete="off"
      />
    </div>
  );
}
