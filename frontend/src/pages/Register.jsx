import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.js";
import { getApiErrorMessage } from "../utils/apiError.js";

export default function Register() {
  const navigate = useNavigate();
  const { registerMutation } = useAuth();
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await registerMutation.mutateAsync(form);
      navigate("/login");
    } catch {
      return;
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl">Create account</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Full name"
          value={form.full_name}
          onChange={(event) => setForm({ ...form, full_name: event.target.value })}
          className="w-full px-4 py-3 rounded-xl border border-slate-200"
        />
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
          disabled={registerMutation.isPending}
          className="w-full px-4 py-3 rounded-xl bg-ember text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {registerMutation.isPending ? "Creating..." : "Create account"}
        </button>
      </form>
      {registerMutation.isError && (
        <p className="text-sm text-red-600">
          {getApiErrorMessage(registerMutation.error, "Registration failed. Try again.")}
        </p>
      )}
      <p className="text-sm text-slate-500">
        Already have an account? <a href="/login" className="text-ember">Sign in</a>
      </p>
    </div>
  );
}
