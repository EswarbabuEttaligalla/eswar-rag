const defaultApiBasePath = import.meta.env.VITE_API_BASE_PATH ?? "/api/v1";

export function getApiBaseUrl() {
  const apiUrl = import.meta.env.VITE_API_URL?.trim();
  if (!apiUrl) {
    return defaultApiBasePath;
  }

  return new URL(defaultApiBasePath, apiUrl).toString().replace(/\/$/, "");
}
