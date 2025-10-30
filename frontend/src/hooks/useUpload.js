import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadDocument } from "../services/documents.js";

export function useUpload() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    }
  });
}
