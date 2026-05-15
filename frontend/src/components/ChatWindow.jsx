import { useEffect, useState } from "react";
import { useChat } from "../hooks/useChat.js";
import { useChatStore } from "../store/chatStore.js";
import { useAuthStore } from "../store/authStore.js";
import MessageBubble from "./MessageBubble.jsx";

export default function ChatWindow() {
  const { messages } = useChatStore();
  const { loadChats, sendMessage } = useChat();
  const { initialized, token } = useAuthStore();
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!initialized || !token) return;
    loadChats().catch(() => setError("Could not load chat history right now."));
  }, [initialized, token]);

  const handleSend = async () => {
    if (!input.trim()) return;
    setSending(true);
    setError("");
    const text = input.trim();
    setInput("");
    try {
      await sendMessage(text);
    } catch {
      setError("Could not send that message right now.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 h-full">
      <div className="flex-1 space-y-4 overflow-y-auto pr-2">
        {messages.length === 0 ? (
          <div className="text-sm text-slate-500">
            Ask a question after uploading a document to see a cited answer here.
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              role={message.role}
              content={message.content}
              sources={message.sources}
            />
          ))
        )}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              handleSend();
            }
          }}
          placeholder="Ask anything about your documents"
          disabled={sending}
          className="flex-1 px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-200"
        />
        <button
          onClick={handleSend}
          disabled={sending || !input.trim()}
          className="px-5 py-3 rounded-xl bg-ember text-white"
        >
          {sending ? "..." : "Send"}
        </button>
      </div>
      {error && <div className="text-sm text-red-600">{error}</div>}
    </div>
  );
}
