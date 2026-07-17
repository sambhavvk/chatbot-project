"use client";

interface MessageBubbleProps {
  type: "user" | "bot";
  text: string;
  meta?: {
    intent: string;
    confidence: number;
  };
}

export function MessageBubble({ type, text, meta }: MessageBubbleProps) {
  const isUser = type === "user";

  return (
    <div
      className={`flex gap-3 animate-fade-in ${
        isUser ? "flex-row-reverse" : "flex-row"
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-lg shadow-md ${
          isUser
            ? "bg-gradient-to-br from-primary-light to-accent"
            : "bg-gradient-to-br from-gray-700 to-gray-800"
        }`}
      >
        {isUser ? "👤" : "🤖"}
      </div>

      {/* Message content */}
      <div
        className={`max-w-[75%] ${isUser ? "items-end" : "items-start"}`}
      >
        <div
          className={`px-4 py-3 rounded-2xl shadow-sm ${
            isUser
              ? "bg-gradient-to-r from-primary to-primary-dark text-white rounded-tr-md"
              : "bg-white text-gray-800 rounded-tl-md border border-gray-100"
          }`}
        >
          <p
            className="text-sm leading-relaxed whitespace-pre-wrap"
            dangerouslySetInnerHTML={{
              __html: text
                .replace(/&/g, "&")
                .replace(/</g, "<")
                .replace(/>/g, ">")
                .replace(/\n/g, "<br>")
                .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>"),
            }}
          />
        </div>

        {/* Metadata */}
        {meta && (
          <div className="mt-1 px-2 text-xs text-gray-400">
            intent: {meta.intent} | confidence:{" "}
            {(meta.confidence * 100).toFixed(0)}%
          </div>
        )}
      </div>
    </div>
  );
}