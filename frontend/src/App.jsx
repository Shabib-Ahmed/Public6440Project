import { useState } from "react";
import PatientLoader from "./components/PatientLoader";
import RiskForm from "./components/RiskForm";
import RiskResult from "./components/RiskResult";

export default function App() {
  const [patientData, setPatientData] = useState(null);
  const [riskResult, setRiskResult] = useState(null);

  return (
    <div className="app-shell">
      <div className="app">
        <header className="hero">
          <h1>Cardiac Risk Calculator</h1>
          <p>
            10-year cardiovascular risk dashboard with FHIR patient loading and editable clinical inputs
          </p>
          {patientData?.name && (
            <div className="patient-banner">
              Loaded patient: <strong>{patientData.name}</strong>
            </div>
          )}
        </header>

        <main className="layout">
          <div className="left-column">
            <PatientLoader onPatientLoaded={setPatientData} />
            <RiskForm prefill={patientData} onResult={setRiskResult} />
          </div>

          <div className="right-column">
            {riskResult ? (
              <RiskResult result={riskResult} />
            ) : (
              <section className="card empty-state">
                <h2>No result yet</h2>
                <p>Load a patient or enter clinical inputs, then calculate the risk score.</p>
              </section>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}