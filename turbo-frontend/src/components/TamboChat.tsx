import Chat from "@tambo-ai/react";

export default function TamboChat() {
  return (
    <div style={{ height: "100vh" }}>
      <Chat apiKey={import.meta.env.VITE_TAMBO_API_KEY} />
    </div>
  );
}
