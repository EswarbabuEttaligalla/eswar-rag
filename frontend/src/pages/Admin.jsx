import { useQuery } from "@tanstack/react-query";
import Loader from "../components/Loader.jsx";
import { listUsers } from "../services/users.js";

export default function Admin() {
  const usersQuery = useQuery({
    queryKey: ["users"],
    queryFn: () => listUsers().then((res) => res.data)
  });

  if (usersQuery.isLoading) {
    return <Loader />;
  }

  return (
    <div className="bg-white border border-slate-200 rounded-3xl p-6">
      <h3 className="text-lg mb-4">User Directory</h3>
      <div className="space-y-3 text-sm">
        {usersQuery.data?.map((user) => (
          <div key={user.id} className="flex items-center justify-between">
            <div>
              <div className="font-medium">{user.email}</div>
              <div className="text-xs text-slate-500">{user.role}</div>
            </div>
            <span className="text-xs text-slate-400">{user.is_active ? "active" : "inactive"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
