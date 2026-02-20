import axios from "axios";
import { API_BASE_URL } from "./axios";

const authClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

const getData = (response) => response.data;

export const authService = {
  login(payload) {
    return authClient.post("/auth/login", payload).then(getData);
  },
  refresh() {
    return authClient.post("/auth/refresh").then(getData);
  },
  logout() {
    return authClient.post("/auth/logout").then(getData);
  },
  me() {
    return authClient.get("/auth/me").then(getData);
  },
};
