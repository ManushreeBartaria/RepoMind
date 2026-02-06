import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeRepo } from "../api/repomindApi";
import { useRepoStore } from "../store/useRepoStore";

export default function UploadRepoPage() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const setRepoId = useRepoStore((s) => s.setRepoId);
  const setFileTree = useRepoStore((s) => s.setFileTree);

  const navigate = useNavigate();

  async function handleAnalyze() {
    if (!repoUrl.trim()) return;

    setLoading(true);
    try {
      const data = await analyzeRepo(repoUrl);
      setRepoId(data.repo_id);
      setFileTree(data.file_tree);
      navigate("/chat");
    } catch (e) {
      alert("Repo analysis failed. Check backend running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 30 }}>
      <h1 style={{ fontSize: 30 }}>RepoMind</h1>
      <p style={{ color: "#555" }}>
        Upload your repository and start chatting with it.
      </p>

      <input
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        placeholder="https://github.com/user/repo"
        style={{
          width: "70%",
          padding: 12,
          borderRadius: 8,
          border: "1px solid #ccc"
        }}
      />

      <button
        onClick={handleAnalyze}
        disabled={loading}
        style={{
          marginLeft: 10,
          padding: "12px 18px",
          borderRadius: 8,
          border: "none",
          background: "#2563eb",
          color: "white"
        }}
      >
        {loading ? "Analyzing..." : "Analyze Repo"}
      </button>
    </div>
  );
}
