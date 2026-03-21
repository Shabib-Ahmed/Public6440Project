import { useState } from "react";
import PatientLoader from "./components/PatientLoader";
import RiskForm from "./components/RiskForm";
import RiskResult from "./components/RiskResult";

export default function App() {
  const [patientData, setPatientData] = useState(null);
  const [riskResult, setRiskResult] = useState(null);

  return (
    <div className="app">
      <header>
        <h1>Cardiac Risk Calculator</h1>
        <p>10-year cardiovascular risk — AHA PREVENT equations</p>
      </header>

      <main>
        <PatientLoader onPatientLoaded={setPatientData} />

        <RiskForm
          prefill={patientData}
          onResult={setRiskResult}
        />

        {riskResult && <RiskResult result={riskResult} />}
      </main>
    </div>
  );
}
