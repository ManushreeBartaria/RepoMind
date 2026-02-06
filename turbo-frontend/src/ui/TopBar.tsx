import { useNavigate } from "react-router-dom";
import { useRepoStore } from "../store/useRepoStore";

export default function TopBar() {
  const navigate = useNavigate();
  const starCurrentChat = useRepoStore((s) => s.starCurrentChat);

  return (
    <div
      style={{
        height: 55,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 16px",
        borderBottom: "1px solid #ddd"
      }}
    >
      <b style={{ fontSize: 18 }}>RepoMind</b>

      <div style={{ display: "flex", gap: 10 }}>
        <button
          onClick={() => starCurrentChat("Saved Chat " + new Date().toLocaleString())}
          style={{
            padding: "8px 12px",
            borderRadius: 8,
            border: "1px solid #ccc",
            background: "white"
          }}
        >
          ⭐ Star Chat
        </button>

        <button
          onClick={() => navigate("/starred")}
          style={{
            padding: "8px 12px",
            borderRadius: 8,
            border: "1px solid #ccc",
            background: "white"
          }}
        >
          📌 Starred
        </button>

        <button
          onClick={() => navigate("/")}
          style={{
            padding: "8px 12px",
            borderRadius: 8,
            border: "1px solid #ccc",
            background: "white"
          }}
        >
          🏠 Home
        </button>
      </div>
    </div>
  );
}
