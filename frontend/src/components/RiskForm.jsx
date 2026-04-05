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

const FIELD_RULES = {
  age:             { min: 30,  max: 79,    unit: "",              label: "Age" },
  totalCholesterol:{ min: 20,  max: 1200,  unit: "mg/dL",         label: "Total cholesterol" },
  hdlCholesterol:  { min: 2,   max: 200,   unit: "mg/dL",         label: "HDL cholesterol" },
  systolicBP:      { min: 40,  max: 320,   unit: "mmHg",          label: "Systolic BP" },
  egfr:            { min: 1,   max: 150,   unit: "mL/min/1.73m²", label: "eGFR" },
  urineAcr:        { min: 0,   max: 15000, unit: "mg/g",          label: "Urine ACR" },
};

function validateForm(form) {
  const errors = {};

  for (const [field, rule] of Object.entries(FIELD_RULES)) {
    const raw = form[field];
    if (raw === "" || raw === null || raw === undefined) continue; // optional fields skip

    const num = Number(raw);
    if (isNaN(num)) {
      errors[field] = `${rule.label} must be a number`;
      continue;
    }
    if (num < rule.min || num > rule.max) {
      errors[field] = `${rule.label}: expected ${rule.min}–${rule.max}${rule.unit ? " " + rule.unit : ""} (got ${num})`;
    }
  }

  // Required fields
  for (const field of ["age", "totalCholesterol", "hdlCholesterol", "systolicBP"]) {
    if (form[field] === "" || form[field] === null || form[field] === undefined) {
      errors[field] = `${FIELD_RULES[field].label} is required`;
    }
  }

  // Cross-field: HDL must be less than total cholesterol
  const hdl = Number(form.hdlCholesterol);
  const tc = Number(form.totalCholesterol);
  if (!isNaN(hdl) && !isNaN(tc) && tc > 0 && hdl >= tc) {
    errors.hdlCholesterol = `HDL (${hdl}) must be less than total cholesterol (${tc})`;
  }

  return errors;
}

export default function RiskForm({ prefill, onResult }) {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [fieldErrors, setFieldErrors] = useState({});
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
    const newForm = { ...form, [name]: type === "checkbox" ? checked : value };
    setForm(newForm);
    // Re-validate only the touched field (and HDL/TC together)
    const errs = validateForm(newForm);
    setFieldErrors((prev) => {
      const next = { ...prev };
      if (errs[name]) next[name] = errs[name];
      else delete next[name];
      // keep HDL cross-field error in sync
      if (name === "hdlCholesterol" || name === "totalCholesterol") {
        if (errs.hdlCholesterol) next.hdlCholesterol = errs.hdlCholesterol;
        else delete next.hdlCholesterol;
      }
      return next;
    });
  }

  async function handleSubmit() {
    const errs = validateForm(form);
    if (Object.keys(errs).length > 0) {
      setFieldErrors(errs);
      return;
    }
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
          <input name="age" type="number" min="30" max="79" value={form.age} onChange={handleChange} />
          {fieldErrors.age && <span className="field-error">{fieldErrors.age}</span>}
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
          <input name="totalCholesterol" type="number" min="20" max="1200" value={form.totalCholesterol} onChange={handleChange} />
          {fieldErrors.totalCholesterol && <span className="field-error">{fieldErrors.totalCholesterol}</span>}
        </label>

        <label>
          HDL cholesterol (mg/dL)
          <input name="hdlCholesterol" type="number" min="2" max="200" value={form.hdlCholesterol} onChange={handleChange} />
          {fieldErrors.hdlCholesterol && <span className="field-error">{fieldErrors.hdlCholesterol}</span>}
        </label>

        <label>
          Systolic BP (mmHg)
          <input name="systolicBP" type="number" min="40" max="320" value={form.systolicBP} onChange={handleChange} />
          {fieldErrors.systolicBP && <span className="field-error">{fieldErrors.systolicBP}</span>}
        </label>

        <label>
          eGFR (optional, mL/min/1.73m²)
          <input name="egfr" type="number" min="1" max="150" value={form.egfr} onChange={handleChange} />
          {fieldErrors.egfr && <span className="field-error">{fieldErrors.egfr}</span>}
        </label>

        <label>
          Urine ACR (optional, mg/g)
          <input name="urineAcr" type="number" min="0" max="15000" value={form.urineAcr} onChange={handleChange} />
          {fieldErrors.urineAcr && <span className="field-error">{fieldErrors.urineAcr}</span>}
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