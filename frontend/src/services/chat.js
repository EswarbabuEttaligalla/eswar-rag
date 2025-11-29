import api from "./api.js";

export const createChat = (payload) => api.post("/chat", payload);
export const listChats = () => api.get("/chat/");
export const listMessages = (chatId) => api.get(`/chat/${chatId}/messages`);
export const askChat = (chatId, payload) => api.post(`/chat/${chatId}/ask`, payload);
