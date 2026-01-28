export default function StarFiles({ selectedFile }) {
  return (
    <div style={{ padding: 16 }}>
      <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>
        Star Files {selectedFile && `- ${selectedFile}`}
      </h2>

      <div
        style={{
          background: "#1e293b",
          padding: 20,
          borderRadius: 8,
          minHeight: 300,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#64748b",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>⭐</div>
          <div>Important files</div>
        </div>
      </div>
    </div>
  );
}
