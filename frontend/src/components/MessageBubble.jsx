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
          <div className="mt-3 space-y-2 text-xs text-slate-500">
            <div className="font-medium text-slate-600">Sources</div>
            <ul className="space-y-1">
              {sources.slice(0, 3).map((source, index) => (
                <li key={`${source.document_id}-${source.chunk_id}-${index}`}>
                  [{index + 1}] {source.document_id}
                  {source.chunk_id ? ` / ${source.chunk_id}` : ""}
                  {typeof source.score === "number" ? ` - ${source.score.toFixed(3)}` : ""}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
