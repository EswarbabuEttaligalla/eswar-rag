import { useMutation } from "@tanstack/react-query";
import { login, logout, register } from "../services/auth.js";
import { getMe } from "../services/users.js";
import { useAuthStore } from "../store/authStore.js";

export function useAuth() {
  const { setAuth, clearAuth } = useAuthStore();

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: async (response) => {
      const { access_token, refresh_token } = response.data;
      setAuth({ accessToken: access_token, refreshToken: refresh_token, user: null });
      try {
        const me = await getMe();
        setAuth({ accessToken: access_token, refreshToken: refresh_token, user: me.data });
      } catch {
        setAuth({ accessToken: access_token, refreshToken: refresh_token, user: null });
      }
    }
  });

  const registerMutation = useMutation({
    mutationFn: register
  });

  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: () => clearAuth()
  });

  return {
    loginMutation,
    registerMutation,
    logoutMutation
  };
}
