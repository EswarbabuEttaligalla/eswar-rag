import api from "./api.js";

export const listUsers = () => api.get("/users");
export const getMe = () => api.get("/users/me");
