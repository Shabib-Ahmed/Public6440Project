import { useState, useEffect } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:5001";

const DEFAULT_FORM = {
  age: "",
  sex: "male",
  totalCholesterol: "",
  hdlCholesterol: "",
  systolicBP: "",
  diabetes: false,
  smoker: false,
  bpTreatment: false,
  egfr: "",
  urineAcr: "",
};

export default function RiskForm({ prefill, onResult }) {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!prefill) return;
    setForm((prev) => ({
      ...prev,
      age: prefill.age ?? prev.age,
      sex: prefill.sex ?? prev.sex,
      totalCholesterol: prefill.total_cholesterol ?? prev.totalCholesterol,
      hdlCholesterol: prefill.hdl_cholesterol ?? prev.hdlCholesterol,
      systolicBP: prefill.systolic_bp ?? prev.systolicBP,
      diabetes: prefill.diabetes ?? prev.diabetes,
      smoker: prefill.smoker ?? prev.smoker,
      bpTreatment: prefill.bp_treatment ?? prev.bpTreatment,
      egfr: prefill.egfr ?? prev.egfr,
      urineAcr: prefill.urine_acr ?? prev.urineAcr,
    }));
  }, [prefill]);

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  async function handleSubmit() {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/risk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          patientId: prefill?.patient_id,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || `Server error: ${res.status}`);
      }

      onResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>Clinical inputs</h2>

      <div className="form-grid">
        <label>
          Age
          <input name="age" type="number" value={form.age} onChange={handleChange} />
        </label>

        <label>
          Sex
          <select name="sex" value={form.sex} onChange={handleChange}>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </label>

        <label>
          Total cholesterol (mg/dL)
          <input name="totalCholesterol" type="number" value={form.totalCholesterol} onChange={handleChange} />
        </label>

        <label>
          HDL cholesterol (mg/dL)
          <input name="hdlCholesterol" type="number" value={form.hdlCholesterol} onChange={handleChange} />
        </label>

        <label>
          Systolic BP (mmHg)
          <input name="systolicBP" type="number" value={form.systolicBP} onChange={handleChange} />
        </label>

        <label>
          eGFR (optional)
          <input name="egfr" type="number" value={form.egfr} onChange={handleChange} />
        </label>

        <label>
          Urine ACR (optional)
          <input name="urineAcr" type="number" value={form.urineAcr} onChange={handleChange} />
        </label>
      </div>

      <div className="checkbox-grid">
        <label className="check-item">
          <input name="diabetes" type="checkbox" checked={form.diabetes} onChange={handleChange} />
          Diabetes
        </label>

        <label className="check-item">
          <input name="smoker" type="checkbox" checked={form.smoker} onChange={handleChange} />
          Current smoker
        </label>

        <label className="check-item">
          <input name="bpTreatment" type="checkbox" checked={form.bpTreatment} onChange={handleChange} />
          On antihypertensive treatment
        </label>
      </div>

      {error && <p className="error-text">{error}</p>}

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Calculating…" : "Calculate risk"}
      </button>
    </section>
  );
}