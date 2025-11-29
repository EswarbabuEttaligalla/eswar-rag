import { create } from "zustand";

export const useChatStore = create((set) => ({
  chats: [],
  activeChatId: null,
  messages: [],
  setChats: (chats) => set({ chats }),
  setActiveChat: (activeChatId) => set({ activeChatId, messages: [] }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] }))
}));
