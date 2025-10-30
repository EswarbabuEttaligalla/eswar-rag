import { useQuery } from "@tanstack/react-query";
import StatCard from "../components/StatCard.jsx";
import Loader from "../components/Loader.jsx";
import { getOverview } from "../services/analytics.js";
import { listDocuments } from "../services/documents.js";
import { useAuthStore } from "../store/authStore.js";

export default function Dashboard() {
  const { user, token, initialized } = useAuthStore();
  const isAdmin = user?.role === "admin";
  const overviewQuery = useQuery({
    queryKey: ["overview"],
    queryFn: () => getOverview().then((res) => res.data),
    enabled: initialized && isAdmin && Boolean(token)
  });
  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: () => listDocuments().then((res) => res.data),
    enabled: initialized && Boolean(token)
  });

  if (isAdmin && overviewQuery.isLoading) {
    return <Loader />;
  }

  const overview = overviewQuery.data || {
    total_users: 0,
    total_documents: documentsQuery.data?.length || 0,
    total_queries: 0,
    avg_latency_ms: 0
  };

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-3 gap-4">
        <StatCard label="Users" value={overview.total_users} />
        <StatCard label="Documents" value={overview.total_documents} />
        <StatCard label="Queries" value={overview.total_queries} />
      </div>
      <div className="bg-white border border-slate-200 rounded-3xl p-6">
        <h3 className="text-lg mb-4">Recent Documents</h3>
        {documentsQuery.isLoading ? (
          <Loader />
        ) : (
          <div className="space-y-3 text-sm">
            {documentsQuery.data?.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{doc.metadata?.original_name || doc.filename}</div>
                  <div className="text-xs text-slate-500">{doc.status}</div>
                </div>
                <span className="text-xs text-slate-400">{doc.size} bytes</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
