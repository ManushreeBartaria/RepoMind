import { ArrowLeft, Folder, FileText, Send } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

import GraphDependency from "../components/GraphDependency";
import ImpactOfChanges from "../components/ImpactOfChanges";
import StarFiles from "../components/StarFiles.jsx";
import ChangedFiles from "../components/ChangedFiles";

export default function Workspace() {
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  // ✅ CHAT STATES
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello! I've analyzed the repository. Ask me about the codebase.",
    },
  ]);
  const [input, setInput] = useState("");

  const tabs = [
    { id: "graph", label: "Graph Dependency", icon: "📊" },
    { id: "impact", label: "Impact of Changes", icon: "⚡" },
    { id: "stars", label: "Star Files", icon: "⭐" },
    { id: "changed", label: "Already Changed Files", icon: "✏️" },
  ];

  // ✅ SEND MESSAGE LOGIC
  function sendMessage() {
    if (!input.trim()) return;

    const userMsg = { sender: "user", text: input };
    const aiMsg = {
      sender: "ai",
      text: `I received your question about "${input}". (AI response will come here)`,
    };

    setMessages((prev) => [...prev, userMsg, aiMsg]);
    setInput("");
  }

  return (
    <div
      style={{
        height: "100vh",
        background: "#020617",
        color: "#e5e7eb",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* TOP BAR */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
          padding: "14px 24px",
          borderBottom: "1px solid #1e293b",
        }}
      >
        <button
          onClick={() => navigate("/")}
          style={{
            background: "transparent",
            border: "none",
            color: "#cbd5f5",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: 6,
            fontSize: 14,
          }}
        >
          <ArrowLeft size={16} /> Back
        </button>

        <span style={{ fontWeight: 500, fontSize: 14 }}>
          ManushreeBartaria / TrickIT.git
        </span>
      </div>

      {/* TABS */}
      <div
        style={{
          display: "flex",
          borderBottom: "2px solid #1e293b",
          background: "#0f172a",
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() =>
              setActiveTab((prev) => (prev === tab.id ? null : tab.id))
            }
            style={{
              flex: 1,
              padding: "12px 16px",
              border: "none",
              background: activeTab === tab.id ? "#1e293b" : "transparent",
              color: activeTab === tab.id ? "#3b82f6" : "#64748b",
              cursor: "pointer",
              fontSize: 13,
              fontWeight: activeTab === tab.id ? 600 : 400,
              borderBottom:
                activeTab === tab.id ? "2px solid #3b82f6" : "none",
            }}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* MAIN AREA */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "300px 1fr",
          flex: 1,
          overflow: "hidden",
        }}
      >
        {/* FILE TREE */}
        <div
          style={{
            background: "#0f172a",
            borderRight: "1px solid #1e293b",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <h3
            style={{
              padding: "12px 16px",
              fontSize: 13,
              fontWeight: 600,
              borderBottom: "1px solid #1e293b",
              margin: 0,
            }}
          >
            File Tree
          </h3>

          <div style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
            <TreeItem name="src" onClick={() => setSelectedFile("src")} selected={selectedFile === "src"} />
            <TreeItem name="components" indent onClick={() => setSelectedFile("components")} selected={selectedFile === "components"} />
            <TreeItem name="Header.tsx" indent file onClick={() => setSelectedFile("Header.tsx")} selected={selectedFile === "Header.tsx"} />
            <TreeItem name="Footer.tsx" indent file onClick={() => setSelectedFile("Footer.tsx")} selected={selectedFile === "Footer.tsx"} />
            <TreeItem name="pages" onClick={() => setSelectedFile("pages")} selected={selectedFile === "pages"} />
            <TreeItem name="Index.tsx" indent file onClick={() => setSelectedFile("Index.tsx")} selected={selectedFile === "Index.tsx"} />
            <TreeItem name="utils" onClick={() => setSelectedFile("utils")} selected={selectedFile === "utils"} />
            <TreeItem name="helpers.ts" indent file onClick={() => setSelectedFile("helpers.ts")} selected={selectedFile === "helpers.ts"} />
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {/* ANALYSIS PANEL */}
          {activeTab && (
            <div
              style={{
                flex: 1,
                overflow: "auto",
                background: "#020617",
                borderBottom: "1px solid #1e293b",
              }}
            >
              {activeTab === "graph" && <GraphDependency selectedFile={selectedFile} />}
              {activeTab === "impact" && <ImpactOfChanges selectedFile={selectedFile} />}
              {activeTab === "stars" && <StarFiles selectedFile={selectedFile} />}
              {activeTab === "changed" && <ChangedFiles selectedFile={selectedFile} />}
            </div>
          )}

          {/* CHAT */}
          <div
            style={{
              background: "#0f172a",
              borderTop: "1px solid #1e293b",
              padding: "12px 16px",
              display: "flex",
              flexDirection: "column",
              flex: activeTab ? "0 0 250px" : "1",
              transition: "flex 0.3s ease",
            }}
          >
            <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 10 }}>
              Chat
            </h3>

            <div
              style={{
                flex: 1,
                overflowY: "auto",
                marginBottom: 10,
                display: "flex",
                flexDirection: "column",
                gap: 8,
              }}
            >
              {messages.map((msg, i) => (
                <div
                  key={i}
                  style={{
                    alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                    background: msg.sender === "user" ? "#2563eb" : "#1e293b",
                    color: msg.sender === "user" ? "#fff" : "#94a3b8",
                    padding: "10px 12px",
                    borderRadius: 8,
                    fontSize: 12,
                    maxWidth: "70%",
                  }}
                >
                  {msg.text}
                </div>
              ))}
            </div>

            <div style={{ display: "flex", gap: 8 }}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Ask about the codebase..."
                style={{
                  flex: 1,
                  padding: "10px 12px",
                  borderRadius: 6,
                  border: "1px solid #334155",
                  background: "#020617",
                  color: "#e5e7eb",
                  outline: "none",
                  fontSize: 12,
                }}
              />
              <button
                onClick={sendMessage}
                style={{
                  padding: "10px 12px",
                  borderRadius: 6,
                  background: "#2563eb",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                <Send size={14} color="white" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function TreeItem({ name, indent, file, onClick, selected }) {
  return (
    <div
      onClick={onClick}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        marginLeft: indent ? 20 : 8,
        padding: "6px 8px",
        color: selected ? "#3b82f6" : "#cbd5f5",
        cursor: "pointer",
        fontSize: 12,
        borderLeft: selected ? "2px solid #3b82f6" : "2px solid transparent",
        background: selected ? "rgba(59,130,246,0.1)" : "transparent",
      }}
    >
      {file ? <FileText size={12} /> : <Folder size={12} />}
      {name}
    </div>
  );
}
