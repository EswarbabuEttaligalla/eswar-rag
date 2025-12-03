import api from "./api.js";

export const getOverview = () => api.get("/analytics/overview");
