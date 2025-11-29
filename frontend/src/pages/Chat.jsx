import { useQuery } from "@tanstack/react-query";
import ChatWindow from "../components/ChatWindow.jsx";
import UploadPanel from "../components/UploadPanel.jsx";
import FileList from "../components/FileList.jsx";
import Loader from "../components/Loader.jsx";
import { listDocuments } from "../services/documents.js";
import { useAuthStore } from "../store/authStore.js";

export default function Chat() {
  const { token, initialized } = useAuthStore();
  const { data, isLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: () => listDocuments().then((res) => res.data),
    enabled: initialized && Boolean(token)
  });

  return (
    <div className="grid lg:grid-cols-[2fr_1fr] gap-6">
      <div className="bg-white border border-slate-200 rounded-3xl p-6 min-h-[70vh]">
        <ChatWindow />
      </div>
      <div className="flex flex-col gap-4">
        <UploadPanel />
        {isLoading ? <Loader /> : <FileList documents={data} />}
      </div>
    </div>
  );
}
