export default function FileList({ documents }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-4">
      <h3 className="text-lg mb-3">Recent Files</h3>
      <div className="space-y-2 text-sm">
        {documents?.length ? (
          documents.map((doc) => (
            <div key={doc.id} className="flex items-center justify-between">
              <div>
                <div className="font-medium">{doc.metadata?.original_name || doc.filename}</div>
                <div className="text-xs text-slate-500">{doc.status}</div>
              </div>
              <span className="text-xs text-slate-400">{doc.size} bytes</span>
            </div>
          ))
        ) : (
          <div className="text-slate-500">No files yet.</div>
        )}
      </div>
    </div>
  );
}