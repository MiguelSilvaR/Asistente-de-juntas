import { useState } from "react";

export function ChatInput({ onSend }: { onSend: (text: string) => void }) {
  const [text, setText] = useState("");

  function handleSend() {
    if (!text.trim()) return;
    onSend(text.trim());
    setText("");
  }

  return (
    <div className="border-t p-4 bg-white flex gap-2">
      <textarea
        className="flex-1 p-3 border rounded-lg focus:outline-none resize-none h-14"
        placeholder="Escribe tu mensaje..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
      />
      <button
        onClick={handleSend}
        className="px-4 bg-black text-white rounded-lg disabled:opacity-50"
      >
        Enviar
      </button>
    </div>
  );
}
