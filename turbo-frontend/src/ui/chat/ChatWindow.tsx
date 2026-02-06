import { useRepoStore } from "../../store/useRepoStore";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";

export default function ChatWindow() {
  const messages = useRepoStore((s) => s.messages);

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ flex: 1, overflowY: "auto", padding: 12 }}>
        {messages.length === 0 ? (
          <p style={{ color: "#666" }}>
            Ask something like: <b>"Explain repo structure"</b>
          </p>
        ) : (
          messages.map((m) => <ChatMessage key={m.id} msg={m} />)
        )}
      </div>
      <ChatInput />
    </div>
  );
}
