export function getApiErrorMessage(error, fallbackMessage) {
  const uploadError = error?.response?.data?.error;
  if (typeof uploadError === "string" && uploadError.trim()) {
    return uploadError;
  }

  const detail = error?.response?.data?.detail;
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  const message = error?.response?.data?.message;
  if (typeof message === "string" && message.trim()) {
    return message;
  }

  if (typeof error?.message === "string" && error.message.trim()) {
    return error.message;
  }

  return fallbackMessage;
}