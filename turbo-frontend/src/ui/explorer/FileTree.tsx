import { useRepoStore } from "../../store/useRepoStore";
import FileNode from "./FileNode";

export default function FileTree() {
  const fileTree = useRepoStore((s) => s.fileTree);

  if (!fileTree) {
    return <div style={{ padding: 12 }}>No repo loaded</div>;
  }

  return (
    <div style={{ padding: 12 }}>
      <h3 style={{ marginBottom: 10 }}>📁 Explorer</h3>
      <FileNode node={fileTree} level={0} />
    </div>
  );
}
