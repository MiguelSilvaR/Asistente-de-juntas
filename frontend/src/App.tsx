import { MessagesList } from "./components/MessagesList";
import { ChatInput } from "./components/ChatInput";
import { useChatStore } from "./stores/chatStore";

export default function App() {
  const addMessage = useChatStore((s) => s.addMessage);

  async function sendMessage(text: string) {
    // 1) agrega mensaje del usuario
    addMessage({ role: "user", content: text });

    // 2) agrega placeholder del bot para ir rellenando (stream o no stream)
    addMessage({ role: "assistant", content: "" });

    // 3) fake respuesta (sustituye por tu fetch/SSE)
    const reply = await fakeLLM(text);
    useChatStore.setState((state) => {
      const msgs = [...state.messages];
      msgs[msgs.length - 1] = { role: "assistant", content: reply };
      return { messages: msgs };
    });
  }

  return (
    <div className="min-h-[100svh] w-screen bg-[#0e0f11] text-white">
      <div className="grid lg:grid-cols-[280px_1fr] h-[100svh]">
        <aside className="hidden lg:flex flex-col border-r border-white/10 p-3 bg-[#0b0b0c]">
          <div className="text-sm text-white/70">Historial</div>
        </aside>

        <main className="flex flex-col h-full">
            <header className="h-10 flex items-center px-4 border-b border-white/10">
              <span className="text-sm font-medium">Chat</span>
            </header>

            {/* OJO: pb-24 evita que el footer lo tape; overflow-y-auto habilita scroll */}
            <section className="flex-1 overflow-y-auto p-4 pb-24">
              <MessagesList />
            </section>

            {/* Footer normal, sin absolute/fixed (no tapa el scroll) */}
            <footer className="border-t border-white/10 bg-[#0e0f11]">
              <div className="max-w-4xl mx-auto p-3">
                <ChatInput onSend={sendMessage} />
              </div>
            </footer>
        </main>
      </div>
    </div>
  );
}

function fakeLLM(q: string) {
  return new Promise<string>((res) =>
    setTimeout(() => res(`Eco: ${q}`), 600)
  );
}
