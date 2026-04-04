function getRiskColor(category) {
  switch (category) {
    case "Low":
      return "risk-low";
    case "Borderline":
      return "risk-borderline";
    case "Intermediate":
      return "risk-intermediate";
    case "High":
      return "risk-high";
    default:
      return "";
  }
}

export default function RiskResult({ result }) {
  const { riskScore10yr, riskCategory, keyFactors, model } = result;
  const width = `${Math.min(Number(riskScore10yr), 30) / 30 * 100}%`;

  return (
    <section className="card result-card">
      <h2>Your 10-year cardiovascular risk</h2>

      <div className="result-summary">
        <div className="risk-number">{riskScore10yr}%</div>
        <div className={`risk-badge ${getRiskColor(riskCategory)}`}>
          {riskCategory} risk
        </div>
      </div>

      <div className="meter">
        <div className={`meter-fill ${getRiskColor(riskCategory)}`} style={{ width }} />
      </div>

      <p className="muted">
        Model: {model === "prototype-prevent-style" ? "Prototype risk model" : model}
      </p>

      {keyFactors && keyFactors.length > 0 && (
        <>
          <h3>Key risk factors</h3>
          <div className="factor-list">
            {keyFactors.map((f, i) => (
              <div className="factor-card" key={i}>
                <strong>{f.factor}</strong>
                <p>{f.advice}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}