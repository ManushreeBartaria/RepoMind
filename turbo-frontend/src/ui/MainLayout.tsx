import FileTree from "../ui/explorer/FileTree";
import ChatWindow from "../ui/chat/ChatWindow";
import PanelsRenderer from "../ui/panels/PanelsRenderer";
import HoverPreviewPopup from "../ui/viewer/HoverPreviewPopup";
import CodeViewer from "../ui/viewer/CodeViewer";
import TopBar from "./TopBar";

export default function MainLayout() {
  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <TopBar />

      <div style={{ flex: 1, display: "flex" }}>
        <div style={{ width: "22%", borderRight: "1px solid #ddd" }}>
          <FileTree />
        </div>

        <div style={{ width: "48%", borderRight: "1px solid #ddd" }}>
          <ChatWindow />
        </div>

        <div style={{ width: "30%", overflowY: "auto" }}>
          <PanelsRenderer />
        </div>
      </div>

      <CodeViewer />
      <HoverPreviewPopup />
    </div>
  );
}
