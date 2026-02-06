import { useEffect } from "react";
import { useRepoStore } from "../store/useRepoStore";

export default function StarredChatsPage() {
  const loadStarredChats = useRepoStore((s) => s.loadStarredChats);
  const starredChats = useRepoStore((s) => s.starredChats);

  useEffect(() => {
    loadStarredChats();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>⭐ Starred Chats</h2>

      {starredChats.length === 0 ? (
        <p>No starred chats.</p>
      ) : (
        <div style={{ marginTop: 15 }}>
          {starredChats.map((c) => (
            <div
              key={c.chatId}
              style={{
                padding: 12,
                marginBottom: 10,
                border: "1px solid #ddd",
                borderRadius: 10
              }}
            >
              <b>{c.title}</b>
              <div style={{ fontSize: 13, color: "#666" }}>
                Repo: {c.repoId} | Messages: {c.messages.length}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
