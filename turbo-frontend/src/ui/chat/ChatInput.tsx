import { useState } from "react";
import { askRepo } from "../../api/repomindApi";
import { useRepoStore } from "../../store/useRepoStore";

export default function ChatInput() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const repoId = useRepoStore((s) => s.repoId);
  const addMessage = useRepoStore((s) => s.addMessage);
  const setPanels = useRepoStore((s) => s.setPanels);
  const highlightFiles = useRepoStore((s) => s.highlightFiles);
  const setCodeHighlights = useRepoStore((s) => s.setCodeHighlights);

  async function handleSend() {
    if (!repoId || !text.trim() || loading) return;

    setLoading(true);

    const userMsg = {
      id: "m_" + Date.now(),
      role: "user",
      content: text
    };

    addMessage(userMsg);
    setText("");

    try {
      const data = await askRepo(repoId, text);

      addMessage({
        id: "m_" + (Date.now() + 1),
        role: "assistant",
        content: data.reply || "No response"
      });

      if (data.ui) setPanels(data.ui);

      if (data.highlight_files) {
        highlightFiles(data.highlight_files);
      }

      if (data.code_highlights) {
        setCodeHighlights(data.code_highlights.file, data.code_highlights.highlights);
      }
    } catch (e) {
      addMessage({
        id: "m_" + (Date.now() + 2),
        role: "assistant",
        content: "Error: backend not responding."
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 12, borderTop: "1px solid #ddd" }}>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask about this repo..."
        style={{
          width: "78%",
          padding: 12,
          borderRadius: 10,
          border: "1px solid #ccc"
        }}
      />

      <button
        onClick={handleSend}
        disabled={loading}
        style={{
          marginLeft: 10,
          padding: "12px 18px",
          borderRadius: 10,
          border: "none",
          background: "#2563eb",
          color: "white"
        }}
      >
        {loading ? "..." : "Send"}
      </button>
    </div>
  );
}
