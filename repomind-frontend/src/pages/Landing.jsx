import { Github, Network, MessageSquare, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Landing() {
  const navigate = useNavigate();

  // ✅ NEW STATES (logic only, UI unchanged)
  const [repoUrl, setRepoUrl] = useState("");
  const [error, setError] = useState("");

  // ✅ GitHub repo validation
  function isValidGithubRepo(url) {
    const pattern =
      /^(https?:\/\/)?(www\.)?github\.com\/[^\/\s]+\/[^\/\s]+$/;
    return pattern.test(url.trim());
  }

  function handleAnalyze() {
    if (!repoUrl.trim()) {
      setError("Please enter a GitHub repository URL");
      return;
    }

    if (!isValidGithubRepo(repoUrl)) {
      setError("Please enter a valid GitHub repository link");
      return;
    }

    // ✅ valid → go to workspace
    setError("");
    navigate("/workspace", { state: { repoUrl } });
  }

  return (
    <div
      style={{
        height: "100vh",
        backgroundColor: "#0b1220",
        color: "#e5e7eb",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* HEADER */}
      <header
        style={{
          borderBottom: "1px solid #1e293b",
          padding: "16px 40px",
          display: "flex",
          alignItems: "center",
          flexShrink: 0,
        }}
      >
        <span style={{ fontSize: 18, fontWeight: 600 }}>
          🐙 RepoMind
        </span>
      </header>

      {/* HERO */}
      <main
        style={{
          maxWidth: 1100,
          margin: "0 auto",
          padding: "0 24px",
          textAlign: "center",
          flex: 1,
          width: "100%",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "flex-start",
            padding: "40px 0",
          }}
        >
          {/* BADGE */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "6px 16px",
              borderRadius: 999,
              background: "rgba(59,130,246,0.15)",
              color: "#60a5fa",
              fontSize: 14,
              fontWeight: 500,
              marginBottom: 32,
            }}
          >
            ✨ AI-Powered Repository Analysis
          </div>

          {/* TITLE */}
          <h1
            style={{
              fontSize: 50,
              fontWeight: 800,
              lineHeight: 1.1,
              marginBottom: 24,
              color: "#f8fafc",
            }}
          >
            Understand Any Codebase <br />
            <span style={{ color: "#3b82f6" }}>In Seconds</span>
          </h1>

          {/* SUBTITLE */}
          <p
            style={{
              maxWidth: 720,
              margin: "0 auto 40px",
              fontSize: 16,
              color: "#94a3b8",
            }}
          >
            RepoMind uses AI to analyze GitHub repositories, visualize file
            structures, and answer your questions about the code.
            Just paste a link and start exploring.
          </p>

          {/* INPUT + BUTTON */}
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: 12,
              flexWrap: "wrap",
              marginBottom: 8,
            }}
          >
            <input
              value={repoUrl}
              onChange={(e) => {
                setRepoUrl(e.target.value);
                setError("");
              }}
              placeholder="https://github.com/owner/repository"
              style={{
                width: 460,
                padding: "14px 16px",
                borderRadius: 8,
                border: `1px solid ${error ? "#ef4444" : "#334155"}`,
                background: "#020617",
                color: "#e5e7eb",
                outline: "none",
              }}
            />

            <button
              onClick={handleAnalyze}
              style={{
                padding: "14px 28px",
                borderRadius: 8,
                border: "none",
                background: "#2563eb",
                color: "#fff",
                fontWeight: 600,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              Analyze <ArrowRight size={18} />
            </button>
          </div>

          {/* ERROR MESSAGE */}
          {error && (
            <div style={{ color: "#ef4444", fontSize: 14, marginBottom: 16 }}>
              {error}
            </div>
          )}

          <p style={{ marginBottom: 32, fontSize: 14, color: "#64748b" }}>
            Works with any public GitHub repository
          </p>

          {/* FEATURES — SAME AS BEFORE */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: 24,
            }}
          >
            <Feature
              icon={<Github size={28} />}
              title="Paste GitHub Link"
              desc="Simply paste any public GitHub repository URL to get started"
            />
            <Feature
              icon={<Network size={28} />}
              title="Visualize Structure"
              desc="See the complete file tree and understand how files connect"
            />
            <Feature
              icon={<MessageSquare size={28} />}
              title="Ask Questions"
              desc="Chat with AI to understand any part of the codebase"
            />
          </div>
        </div>
      </main>

      {/* FOOTER */}
      <footer
        style={{
          borderTop: "1px solid #1e293b",
          padding: 16,
          textAlign: "center",
          fontSize: 14,
          color: "#64748b",
          flexShrink: 0,
        }}
      >
        RepoMind — AI-powered repository analysis
      </footer>
    </div>
  );
}

function Feature({ icon, title, desc }) {
  return (
    <div
      style={{
        background: "#0f172a",
        border: "1px solid #334155",
        borderRadius: 14,
        padding: 24,
        textAlign: "center",
      }}
    >
      <div style={{ color: "#3b82f6", marginBottom: 16 }}>{icon}</div>
      <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
        {title}
      </h3>
      <p style={{ fontSize: 14, color: "#94a3b8" }}>{desc}</p>
    </div>
  );
}
