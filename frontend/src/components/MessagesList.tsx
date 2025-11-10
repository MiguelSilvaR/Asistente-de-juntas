import { ChatMessage } from "./ChatMessage";
import { useChatStore } from "../stores/chatStore";

export function MessagesList() {
  const messages = useChatStore((s) => s.messages);

  return (
    <div className="flex flex-col gap-3 p-4 overflow-y-auto flex-1">
      {messages.map((m, i) => (
        <ChatMessage key={i} role={m.role} content={m.content} />
      ))}
    </div>
  );
}
