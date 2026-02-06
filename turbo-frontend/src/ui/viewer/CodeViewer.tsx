import { useEffect, useState } from "react";
import { useRepoStore } from "../../store/useRepoStore";
import { fetchFile } from "../../api/repomindApi";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";

export default function CodeViewer() {
  const repoId = useRepoStore((s) => s.repoId);
  const selectedFile = useRepoStore((s) => s.selectedFile);
  const setSelectedFile = useRepoStore((s) => s.setSelectedFile);
  const codeHighlights = useRepoStore((s) => s.codeHighlights);

  const [content, setContent] = useState("");

  useEffect(() => {
    async function load() {
      if (!repoId || !selectedFile) return;

      const data = await fetchFile(repoId, selectedFile);
      setContent(data.content || "");
    }

    load();
  }, [repoId, selectedFile]);

  if (!selectedFile) return null;

  const highlights = codeHighlights[selectedFile] || [];

  const lines = content.split("\n");

  return (
    <div
      style={{
        position: "fixed",
        left: 0,
        right: 0,
        bottom: 0,
        height: "40vh",
        background: "white",
        borderTop: "2px solid #ddd",
        zIndex: 9998,
        display: "flex",
        flexDirection: "column"
      }}
    >
      <div
        style={{
          padding: 10,
          borderBottom: "1px solid #ddd",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}
      >
        <b>📄 {selectedFile}</b>

        <button
          onClick={() => setSelectedFile(null)}
          style={{
            padding: "6px 12px",
            borderRadius: 8,
            border: "1px solid #ccc",
            background: "white"
          }}
        >
          Close
        </button>
      </div>

      <div style={{ flex: 1, overflow: "auto", padding: 10 }}>
        <SyntaxHighlighter language="python" showLineNumbers>
          {lines
            .map((line, idx) => {
              const lineNo = idx + 1;
              const isImportant = highlights.some(
                (h) => lineNo >= h.start && lineNo <= h.end
              );

              if (isImportant) return ">>> " + line;
              return line;
            })
            .join("\n")}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}
