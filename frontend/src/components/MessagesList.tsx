import { useEffect, useRef } from "react";
import { ChatMessage } from "./ChatMessage";
import { useChatStore } from "../stores/chatStore";

export function MessagesList() {
  const messages = useChatStore((s) => s.messages);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Autoscroll suave al último mensaje
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]); // se dispara cada vez que cambia el número de mensajes

  return (
    <div className="flex flex-col gap-3">
      {messages.map((m, i) => (
        <ChatMessage key={i} role={m.role} content={m.content} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}