import { useState } from "react";
import { useRepoStore } from "../../store/useRepoStore";

export default function FileNode({ node, level }: any) {
  const [open, setOpen] = useState(true);

  const setSelectedFile = useRepoStore((s) => s.setSelectedFile);
  const setHoveredFile = useRepoStore((s) => s.setHoveredFile);
  const highlightedFiles = useRepoStore((s) => s.fileHighlights);

  const paddingLeft = level * 14;

  if (node.type === "folder") {
    return (
      <div style={{ paddingLeft }}>
        <div
          style={{ cursor: "pointer", fontWeight: 600, marginBottom: 2 }}
          onClick={() => setOpen(!open)}
        >
          {open ? "📂" : "📁"} {node.name}
        </div>

        {open &&
          node.children?.map((child: any) => (
            <FileNode key={child.path} node={child} level={level + 1} />
          ))}
      </div>
    );
  }

  const isHighlighted = node.path && highlightedFiles.includes(node.path);

  return (
    <div
      style={{
        paddingLeft,
        cursor: "pointer",
        marginTop: 2,
        padding: "3px 6px",
        borderRadius: 6,
        background: isHighlighted ? "#fff3cd" : "transparent"
      }}
      onMouseEnter={() => setHoveredFile(node.path)}
      onMouseLeave={() => setHoveredFile(null)}
      onClick={() => setSelectedFile(node.path)}
    >
      📄 {node.name}
    </div>
  );
}
