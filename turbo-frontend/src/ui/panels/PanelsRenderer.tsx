import { useRepoStore } from "../../store/useRepoStore";
import DependencyGraphPanel from "./DependencyGraphPanel";
import ImpactAnalysisPanel from "./ImpactAnalysisPanel";
import RelatedFilesPanel from "./RelatedFilesPanel";

export default function PanelsRenderer() {
  const panels = useRepoStore((s) => s.uiPanels);

  if (!panels.length) {
    return <div style={{ padding: 12 }}>No insights yet.</div>;
  }

  return (
    <div style={{ padding: 12 }}>
      {panels.map((p: any, idx: number) => {
        if (p.type === "dependency_graph") return <DependencyGraphPanel key={idx} data={p.data} />;
        if (p.type === "impact_analysis") return <ImpactAnalysisPanel key={idx} data={p.data} />;
        if (p.type === "related_files") return <RelatedFilesPanel key={idx} data={p.data} />;
        return null;
      })}
    </div>
  );
}
