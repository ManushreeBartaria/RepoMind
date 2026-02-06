export default function RelatedFilesPanel({ data }: any) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 12,
        marginBottom: 18
      }}
    >
      <h3>📌 Related Files</h3>

      <h4>Primary</h4>
      <ul>
        {data.primary?.map((f: string) => (
          <li key={f}>{f}</li>
        ))}
      </ul>

      <h4>Secondary</h4>
      <ul>
        {data.secondary?.map((f: string) => (
          <li key={f}>{f}</li>
        ))}
      </ul>
    </div>
  );
}
