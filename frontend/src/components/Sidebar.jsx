import { NavLink } from "react-router-dom";
import { useAuthStore } from "../store/authStore.js";

const navItems = [
  { to: "/chat", label: "Chat" },
  { to: "/dashboard", label: "Dashboard" }
];

export default function Sidebar() {
  const { user } = useAuthStore();

  return (
    <aside className="bg-white/90 backdrop-blur border-r border-slate-200 p-6 flex flex-col gap-6">
      <div>
        <h2 className="text-2xl">Workspace</h2>
        <p className="text-sm text-slate-600">Enterprise RAG</p>
      </div>
      <nav className="flex flex-col gap-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `px-4 py-2 rounded-xl ${
                isActive ? "bg-ink text-white" : "bg-slate-100 text-slate-700"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
        {user?.role === "admin" && (
          <NavLink
            to="/admin"
            className={({ isActive }) =>
              `px-4 py-2 rounded-xl ${
                isActive ? "bg-ink text-white" : "bg-slate-100 text-slate-700"
              }`
            }
          >
            Admin
          </NavLink>
        )}
      </nav>
      <div className="mt-auto text-xs text-slate-500">Role: {user?.role}</div>
    </aside>
  );
}
