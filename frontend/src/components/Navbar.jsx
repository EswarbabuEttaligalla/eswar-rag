import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "../store/authStore.js";
import { useAuth } from "../hooks/useAuth.js";

export default function Navbar() {
  const navigate = useNavigate();
  const { user, refreshToken, clearAuth } = useAuthStore();
  const { logoutMutation } = useAuth();
  const queryClient = useQueryClient();

  const handleLogout = async () => {
    if (refreshToken) {
      try {
        await logoutMutation.mutateAsync({ refresh_token: refreshToken });
      } finally {
        clearAuth();
        queryClient.clear();
        navigate("/login");
      }
      return;
    }
    clearAuth();
    queryClient.clear();
    navigate("/login");
  };

  return (
    <header className="px-6 py-4 bg-white/80 backdrop-blur border-b border-slate-200 flex items-center justify-between">
      <Link to="/chat" className="text-xl font-semibold">
        Knowledge Assistant
      </Link>
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-600">{user?.email}</span>
        <button
          onClick={handleLogout}
          disabled={logoutMutation.isPending}
          className="px-4 py-2 rounded-full bg-ink text-white text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {logoutMutation.isPending ? "Logging out..." : "Logout"}
        </button>
      </div>
    </header>
  );
}
