import axios from "axios";
import { useAuthStore } from "../store/authStore.js";
import { getApiBaseUrl } from "../utils/apiConfig.js";
import {
  clearAuthStorage,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken
} from "../utils/token.js";

const apiBasePath = getApiBaseUrl();

const api = axios.create({
  baseURL: apiBasePath
});

let isRefreshing = false;
let pendingQueue = [];

function setAuthorizationHeader(config, token) {
  if (!config.headers) {
    config.headers = {};
  }
  if (typeof config.headers.set === "function") {
    config.headers.set("Authorization", `Bearer ${token}`);
    return;
  }
  config.headers.Authorization = `Bearer ${token}`;
}

function resolveQueue(error, token = null) {
  pendingQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else {
      promise.resolve(token);
    }
  });
  pendingQueue = [];
}

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token || getAccessToken();
  if (token) {
    setAuthorizationHeader(config, token);
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({ resolve, reject });
        }).then((token) => {
          setAuthorizationHeader(original, token);
          return api(original);
        });
      }
      original._retry = true;
      isRefreshing = true;
      try {
        const refreshToken = getRefreshToken();
        if (!refreshToken) {
          clearAuthStorage();
          return Promise.reject(error);
        }
        const response = await axios.post(`${apiBasePath}/auth/refresh`, { refresh_token: refreshToken });
        const { access_token, refresh_token } = response.data;
        setAccessToken(access_token);
        setRefreshToken(refresh_token);
        useAuthStore.setState({ token: access_token, refreshToken: refresh_token });
        resolveQueue(null, access_token);
        setAuthorizationHeader(original, access_token);
        return api(original);
      } catch (refreshError) {
        resolveQueue(refreshError, null);
        clearAuthStorage();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export default api;
