import { useEffect, useState } from "react";
import { useRepoStore } from "../../store/useRepoStore";
import { fetchFile } from "../../api/repomindApi";

export default function HoverPreviewPopup() {
  const repoId = useRepoStore((s) => s.repoId);
  const hoveredFile = useRepoStore((s) => s.hoveredFile);

  const [content, setContent] = useState("");

  useEffect(() => {
    async function load() {
      if (!repoId || !hoveredFile) return;

      try {
        const data = await fetchFile(repoId, hoveredFile);
        setContent((data.content || "").slice(0, 800));
      } catch {
        setContent("");
      }
    }

    load();
  }, [repoId, hoveredFile]);

  if (!hoveredFile) return null;

  return (
    <div
      style={{
        position: "fixed",
        bottom: 15,
        left: 15,
        width: 430,
        background: "white",
        border: "1px solid #ddd",
        borderRadius: 12,
        padding: 12,
        boxShadow: "0px 8px 18px rgba(0,0,0,0.2)",
        zIndex: 9999
      }}
    >
      <b style={{ fontSize: 13 }}>{hoveredFile}</b>

      <pre
        style={{
          marginTop: 8,
          fontSize: 12,
          maxHeight: 220,
          overflow: "auto",
          background: "#f9fafb",
          padding: 10,
          borderRadius: 10
        }}
      >
        {content || "No preview available"}
      </pre>
    </div>
  );
}
