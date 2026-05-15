import { useState } from "react";
import { useUpload } from "../hooks/useUpload.js";
import { getApiErrorMessage } from "../utils/apiError.js";

const MAX_UPLOAD_MB = 20;
const ACCEPTED_TYPES = ".pdf,.txt,.docx,.csv";

export default function UploadPanel() {
  const [file, setFile] = useState(null);
  const upload = useUpload();

  const handleUpload = async () => {
    if (!file) return;
    try {
      await upload.mutateAsync(file);
      setFile(null);
    } catch {
      return;
    }
  };

  const uploadError = getApiErrorMessage(upload.error, "Upload failed. Please try again.");
  const fileSizeMb = file ? file.size / (1024 * 1024) : 0;
  const isFileTooLarge = fileSizeMb > MAX_UPLOAD_MB;

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-3">
      <h3 className="text-lg">Upload Documents</h3>
      <input
        type="file"
        accept={ACCEPTED_TYPES}
        onChange={(event) => {
          setFile(event.target.files[0] || null);
        }}
        className="w-full text-sm"
      />
      {file && (
        <div className="text-xs text-slate-500 space-y-1">
          <div>{file.name}</div>
          <div>
            {fileSizeMb.toFixed(2)} MB of {MAX_UPLOAD_MB} MB max
          </div>
        </div>
      )}
      <button
        onClick={handleUpload}
        disabled={!file || upload.isPending || isFileTooLarge}
        className="w-full px-4 py-2 rounded-xl bg-ink text-white disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {upload.isPending ? "Uploading..." : "Upload"}
      </button>
      {isFileTooLarge && <div className="text-sm text-red-600">File is too large.</div>}
      {upload.isError && <div className="text-sm text-red-600">{uploadError}</div>}
    </div>
  );
}
