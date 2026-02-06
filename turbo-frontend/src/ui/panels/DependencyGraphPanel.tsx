import ReactFlow, { Background, Controls } from "reactflow";
import "reactflow/dist/style.css";
import { useRepoStore } from "../../store/useRepoStore";

export default function DependencyGraphPanel({ data }: any) {
  const setHoveredFile = useRepoStore((s) => s.setHoveredFile);

  return (
    <div style={{ marginBottom: 18 }}>
      <h3>🕸 Dependency Graph</h3>

      <div style={{ height: 320, border: "1px solid #ddd", borderRadius: 12 }}>
        <ReactFlow
          nodes={data.nodes || []}
          edges={data.edges || []}
          onNodeMouseEnter={(_, node) => {
            if (node.data?.path) setHoveredFile(node.data.path);
          }}
          onNodeMouseLeave={() => setHoveredFile(null)}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}
