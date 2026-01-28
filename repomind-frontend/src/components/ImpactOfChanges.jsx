export default function ImpactOfChanges({ selectedFile }) {
  const impacts = [
    { file: "Index.tsx", severity: "high", change: "Component signature changed" },
    { file: "Footer.tsx", severity: "medium", change: "Props updated" },
  ];

  return (
    <div style={{ padding: 16 }}>
      <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>
        Impact of Changes {selectedFile && `- ${selectedFile}`}
      </h2>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {impacts.map((item) => (
          <div
            key={item.file}
            style={{
              background: "#1e293b",
              padding: 12,
              borderRadius: 6,
              borderLeft: `3px solid ${item.severity === "high" ? "#ef4444" : "#f59e0b"}`,
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 500, color: "#e5e7eb" }}>
              {item.file}
            </div>
            <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 4 }}>
              {item.change}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}