import { MessagesList } from "./components/MessagesList";
import { ChatInput } from "./components/ChatInput";
import { useChatStore } from "./stores/chatStore";

export default function App() {
  const addMessage = useChatStore((s) => s.addMessage);

  async function sendMessage(text: string) {
    // 1) agrega mensaje del usuario
    addMessage({ role: "user", content: text });

    // 2) agrega placeholder del bot para ir rellenando (stream o no stream)
    addMessage({ role: "assistant", content: "Pensando" });

    // 3) fake respuesta (sustituye por tu fetch/SSE)
    const reply = await execUserOp(text);
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

function execUserOp(q: string) {
  return fetch("http://127.0.0.1:8000/v1/intent/create/parse", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      text: q   // 🔥 campo exacto que tu backend espera
    })
  }).then(async (res) => {
    if (!res.ok)
      return "Por favor, se más claro con tus instrucciones e intenta de nuevo"
    let json_res = await res.json()
    json_res = json_res.intent
    console.log(json_res)
    if (json_res.err != null)
      return json_res.err
    if (json_res.intent == "create") {
      delete json_res.intent
      let create = await fetch("http://127.0.0.1:8000/v1/meetings", 
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(json_res)
        })
        .then(async(cres) => {
          return cres.json()
        }).catch((e) => "Error: " + e)
      return `Se creo exitosamente la junta con el siguiente id: ${create.id}`
    } else if (json_res.intent == "cancel") {
      let cancel = await fetch(`http://127.0.0.1:8000/v1/meetings/${json_res.cancel_id}`, 
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json"
          }
        })
        .then(async(cres) => {
          return cres.json()
        }).catch((e) => "Error: " + e)
      return `Se cancelo exitosamente la junta con el siguiente id: ${cancel.id}`
    } else if (json_res.intent == "update") {
      delete json_res.intent
      let update = await fetch(`http://127.0.0.1:8000/v1/meetings/${json_res.update_id}`, 
              {
                method: "PUT",
                headers: {
                  "Content-Type": "application/json"
                },
                body: JSON.stringify(json_res.fields)
              })
              .then(async(cres) => {
                return cres.json()
              }).catch(async(e) => { return "Error: " + e})
              console.log(update)
      if (update.id === undefined)
        return "Id no encontrado, verifique si es correcto"
      return `Se actualizo exitosamente la junta con el siguiente id: ${update.id}`
    } else if (json_res.intent == "list") {
      let date = json_res.fecha
      let update = await fetch(`http://127.0.0.1:8000/v1/meetings?fecha=${date}`, 
              {
                method: "GET",
                headers: {
                  "Content-Type": "application/json"
                }
              })
              .then(async(cres) => {
                return cres.json()
              }).catch(async(e) => { return "Error: " + e})
              console.log(update)
      let events = update.events;
      
      const lines = events.map((evt:any) => {
        const title = evt.summary || "(Sin título)";

        // Convierte la fecha a formato más legible
        const start = new Date(evt.start.dateTime);
        const end = new Date(evt.end.dateTime);

        const startTime = start.toLocaleTimeString("es-MX", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false
        });

        const endTime = end.toLocaleTimeString("es-MX", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false
        });

        return `• ${title} — de ${startTime} a ${endTime}\n`;
      });

      return [
        "Estas son tus reuniones del día:",
        "",
        ...lines
      ].join("\n");
    } else if (json_res.intent == "free") {
      delete json_res.intent
      let free = await fetch(`http://127.0.0.1:8000/v1/meetings/free`, 
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json"
                },
                body: JSON.stringify(json_res)
              })
              .then(async(fres) => {
                return fres.json()
              }).catch(async(e) => { return "Error: " + e})
              console.log(free)
      const fmt = new Intl.DateTimeFormat("es-MX", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
        timeZone: "America/Mexico_City",
      });

      let text = "Aquí están tus espacios libres del día:\n\n";

      free.slots.forEach(([start, end]:any, index:any) => {
        const startDate = new Date(start);
        const endDate = new Date(end);

        const humanStart = fmt.format(startDate);
        const humanEnd = fmt.format(endDate);

        text += `• De ${humanStart} a ${humanEnd}\n\n`;
      });

      return text;
    } else {
      return "Función aún no soportada"
    }
  })
    .catch(async (err) => {
      return "Hubo un error en tu llamada, intenta más tarde"
    });
}
