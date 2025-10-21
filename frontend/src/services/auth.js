import api from "./api.js";

export const register = (payload) => api.post("/auth/register", payload);
export const login = (payload) => api.post("/auth/login", payload);
export const refresh = (payload) => api.post("/auth/refresh", payload);
export const logout = (payload) => api.post("/auth/logout", payload);
