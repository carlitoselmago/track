import { api } from "./axios";

const getData = (response) => response.data;

export const userService = {
  listUsers() {
    return api.get("/users").then(getData);
  },
  createUser(payload) {
    return api.post("/users", payload).then(getData);
  },
  getEmailPreference() {
    return api.get("/users/me/preferences/email-notifications").then(getData);
  },
  updateEmailPreference(enabled) {
    return api
      .patch("/users/me/preferences/email-notifications", {
        email_notifications_enabled: enabled,
      })
      .then(getData);
  },
  changePassword(newPassword) {
    return api.post("/users/me/password", { new_password: newPassword }).then(getData);
  },
};
