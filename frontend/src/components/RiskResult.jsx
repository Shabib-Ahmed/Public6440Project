export default function RiskResult({ result }) {
  const { riskScore10yr, riskCategory, keyFactors } = result;

  return (
    <section>
      <h2>Your 10-year cardiovascular risk</h2>

      <p>
        <strong>{riskScore10yr}%</strong> — {riskCategory} risk
      </p>

      <div id="risk-chart-placeholder" style={{ height: 200, background: "#f0f0f0" }}>
        Chart goes here (ChartJS)
      </div>

      {keyFactors && keyFactors.length > 0 && (
        <>
          <h3>Key risk factors</h3>
          {keyFactors.map((f, i) => (
            <div key={i}>
              <strong>{f.factor}</strong>
              <p>{f.advice}</p>
            </div>
          ))}
        </>
      )}
    </section>
  );
}
