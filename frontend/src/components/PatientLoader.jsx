import { useState } from "react";

const API_BASE = "http://localhost:5000";

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
    <section>
      <h2>Load patient from FHIR</h2>
      <p>Optional — enter a FHIR patient ID to pre-fill the form below.</p>

      <input
        type="text"
        placeholder="e.g. smart-1234567"
        value={patientId}
        onChange={(e) => setPatientId(e.target.value)}
      />
      <button onClick={handleLoad} disabled={loading}>
        {loading ? "Loading…" : "Load patient"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </section>
  );
}
