export default function MessageBubble({ role, content, sources }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
          isUser ? "bg-ink text-white" : "bg-white border border-slate-200"
        }`}
      >
        <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
        {sources && sources.length > 0 && !isUser && (
          <div className="mt-3 text-xs text-slate-500">
            Sources: {sources.length}
          </div>
        )}
      </div>
    </div>
  );
}
