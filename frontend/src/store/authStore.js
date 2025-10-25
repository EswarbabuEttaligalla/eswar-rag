import axios from "axios";
import { create } from "zustand";
import { getApiBaseUrl } from "../utils/apiConfig.js";
import {
  clearAuthStorage,
  getAccessToken,
  getRefreshToken,
  getUser,
  isTokenExpiringSoon,
  setAccessToken,
  setRefreshToken,
  setUser
} from "../utils/token.js";

const apiBasePath = getApiBaseUrl();

export const useAuthStore = create((set) => ({
  token: getAccessToken(),
  refreshToken: getRefreshToken(),
  user: getUser(),
  initialized: false,
  bootstrapping: false,
  bootstrapAuth: async () => {
    if (useAuthStore.getState().bootstrapping || useAuthStore.getState().initialized) {
      return;
    }
    set({ bootstrapping: true });
    const accessToken = getAccessToken();
    const refreshToken = getRefreshToken();
    const user = getUser();

    if (!refreshToken) {
      set({ token: accessToken, refreshToken: null, user, initialized: true, bootstrapping: false });
      return;
    }

    if (accessToken && !isTokenExpiringSoon(accessToken)) {
      set({ token: accessToken, refreshToken, user, initialized: true, bootstrapping: false });
      return;
    }

    try {
      const response = await axios.post(`${apiBasePath}/auth/refresh`, { refresh_token: refreshToken });
      const { access_token, refresh_token } = response.data;
      setAccessToken(access_token);
      setRefreshToken(refresh_token);
      set({ token: access_token, refreshToken: refresh_token, user, initialized: true, bootstrapping: false });
    } catch {
      clearAuthStorage();
      set({ token: null, refreshToken: null, user: null, initialized: true, bootstrapping: false });
    }
  },
  setAuth: ({ accessToken, refreshToken, user }) => {
    setAccessToken(accessToken);
    setRefreshToken(refreshToken);
    setUser(user);
    set({ token: accessToken, refreshToken, user, initialized: true, bootstrapping: false });
  },
  clearAuth: () => {
    clearAuthStorage();
    set({ token: null, refreshToken: null, user: null, initialized: true, bootstrapping: false });
  }
}));
