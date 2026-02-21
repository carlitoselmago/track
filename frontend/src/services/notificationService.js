import { api } from "./axios";

const getData = (response) => response.data;

export const notificationService = {
  list() {
    return api.get("/notifications").then(getData);
  },
  markAllRead() {
    return api.post("/notifications/read-all").then(getData);
  },
  deleteOne(notificationId) {
    return api.delete(`/notifications/${notificationId}`).then(getData);
  },
  clearAll() {
    return api.delete("/notifications").then(getData);
  },
};
