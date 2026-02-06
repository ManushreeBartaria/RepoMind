export default function ChatMessage({ msg }: any) {
  const isUser = msg.role === "user";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: 10
      }}
    >
      <div
        style={{
          maxWidth: "80%",
          padding: 12,
          borderRadius: 12,
          background: isUser ? "#dbeafe" : "#f3f4f6"
        }}
      >
        {msg.content}
      </div>
    </div>
  );
}
