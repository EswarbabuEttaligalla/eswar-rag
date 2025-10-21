import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.js";

export default function Login() {
  const navigate = useNavigate();
  const { loginMutation } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await loginMutation.mutateAsync(form);
      navigate("/chat");
    } catch {
      return;
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl">Sign in</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={(event) => setForm({ ...form, email: event.target.value })}
          className="w-full px-4 py-3 rounded-xl border border-slate-200"
        />
        <input
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={(event) => setForm({ ...form, password: event.target.value })}
          className="w-full px-4 py-3 rounded-xl border border-slate-200"
        />
        <button
          type="submit"
          disabled={loginMutation.isPending}
          className="w-full px-4 py-3 rounded-xl bg-ink text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loginMutation.isPending ? "Signing in..." : "Sign in"}
        </button>
      </form>
      {loginMutation.isError && (
        <p className="text-sm text-red-600">Login failed. Check credentials.</p>
      )}
      <p className="text-sm text-slate-500">
        New here? <a href="/register" className="text-ember">Create an account</a>
      </p>
    </div>
  );
}
