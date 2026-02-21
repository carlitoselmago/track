import { api } from "./axios";

const getData = (response) => response.data;

export const timerService = {
  startTimer(cardId) {
    return api.post(`/cards/${cardId}/timer/start`).then(getData);
  },
  stopTimer(cardId) {
    return api.post(`/cards/${cardId}/timer/stop`).then(getData);
  },
  getCardTime(cardId) {
    return api.get(`/cards/${cardId}/time`).then(getData);
  },
  getActiveTimer() {
    return api.get("/users/me/active-timer").then(getData);
  },
  getTimeSessions(cardId) {
    return api.get(`/cards/${cardId}/time-sessions`).then(getData);
  },
  updateTimeSession(sessionId, durationSeconds) {
    return api
      .patch(`/time-sessions/${sessionId}`, { duration_seconds: durationSeconds })
      .then(getData);
  },
  deleteTimeSession(sessionId) {
    return api.delete(`/time-sessions/${sessionId}`).then(getData);
  },
};
