import { useState } from "react";
import { useUpload } from "../hooks/useUpload.js";

export default function UploadPanel() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const upload = useUpload();

  const handleUpload = async () => {
    if (!file) return;
    setError("");
    try {
      await upload.mutateAsync(file);
      setFile(null);
    } catch {
      setError("Upload failed. Please try again.");
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-3">
      <h3 className="text-lg">Upload Documents</h3>
      <input
        type="file"
        accept=".pdf,.txt,.docx,.csv"
        onChange={(event) => {
          setFile(event.target.files[0] || null);
          setError("");
        }}
        className="w-full text-sm"
      />
      <button
        onClick={handleUpload}
        disabled={!file || upload.isPending}
        className="w-full px-4 py-2 rounded-xl bg-ink text-white disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {upload.isPending ? "Uploading..." : "Upload"}
      </button>
      {error && <div className="text-sm text-red-600">{error}</div>}
    </div>
  );
}
