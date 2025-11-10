import { create } from "zustand";

type Message = { role: "user" | "assistant"; content: string };

interface ChatState {
  messages: Message[];
  addMessage: (m: Message) => void;
  clear: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  addMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  clear: () => set({ messages: [] }),
}));
