import { useChatStore } from "../store/chatStore.js";
import { askChat, createChat, listChats, listMessages } from "../services/chat.js";

export function useChat() {
  const {
    chats,
    activeChatId,
    setChats,
    setActiveChat,
    setMessages,
    addMessage
  } = useChatStore();

  const loadChats = async () => {
    const response = await listChats();
    setChats(response.data);
    if (!activeChatId && response.data.length > 0) {
      setActiveChat(response.data[0].id);
      await loadMessages(response.data[0].id);
    }
  };

  const loadMessages = async (chatId) => {
    const response = await listMessages(chatId);
    setMessages(response.data);
  };

  const ensureChat = async () => {
    if (activeChatId) return activeChatId;
    const response = await createChat({ title: "New Chat" });
    setChats([...chats, response.data]);
    setActiveChat(response.data.id);
    return response.data.id;
  };

  const sendMessage = async (text) => {
    const chatId = await ensureChat();
    addMessage({
      id: `local-${Date.now()}`,
      role: "user",
      content: text,
      sources: [],
      created_at: new Date().toISOString()
    });
    try {
      const response = await askChat(chatId, { question: text, top_k: 6 });
      if (!response.data || typeof response.data.answer !== "string") {
        throw new Error("Empty chat response");
      }
      addMessage({
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: response.data.answer,
        sources: response.data.sources,
        created_at: new Date().toISOString()
      });
      return response.data;
    } catch (error) {
      addMessage({
        id: `assistant-error-${Date.now()}`,
        role: "assistant",
        content: "I could not complete that request right now.",
        sources: [],
        created_at: new Date().toISOString()
      });
      throw error;
    }
  };

  return { loadChats, loadMessages, sendMessage };
}
