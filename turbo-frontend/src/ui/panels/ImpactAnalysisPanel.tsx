export default function ImpactAnalysisPanel({ data }: any) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 12,
        marginBottom: 18
      }}
    >
      <h3>⚠ Impact Analysis</h3>

      <p>
        <b>Risk:</b> {data.risk}
      </p>

      <p>
        <b>Reason:</b> {data.reason}
      </p>

      <h4>Affected Files</h4>
      <ul>
        {data.affected_files?.map((f: string) => (
          <li key={f}>{f}</li>
        ))}
      </ul>
    </div>
  );
}
