import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:5001";

export default function PatientLoader({ onPatientLoaded }) {
  const [patientId, setPatientId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleLoad() {
    if (!patientId.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/patient/${patientId.trim()}`);
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      onPatientLoaded(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>Load patient from FHIR</h2>
      <p className="muted">Optional — enter a FHIR patient ID to pre-fill the form below.</p>

      <div className="inline-row">
        <input
          type="text"
          placeholder="Enter FHIR patient ID"
          value={patientId}
          onChange={(e) => setPatientId(e.target.value)}
        />
        <button onClick={handleLoad} disabled={loading}>
          {loading ? "Loading…" : "Load patient"}
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}
    </section>
  );
}