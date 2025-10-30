import api from "./api.js";

export const uploadDocument = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
};

export const listDocuments = () => api.get("/documents/");
export const deleteDocument = (id) => api.delete(`/documents/${id}`);
