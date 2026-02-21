import { api } from "./axios";

const getData = (response) => response.data;

export const cardService = {
  createCard(listId, payload) {
    return api.post(`/lists/${listId}/cards`, payload).then(getData);
  },
  getCard(cardId) {
    return api.get(`/cards/${cardId}`).then(getData);
  },
  updateCard(cardId, payload) {
    return api.patch(`/cards/${cardId}`, payload).then(getData);
  },
  deleteCard(cardId) {
    return api.delete(`/cards/${cardId}`).then(getData);
  },
  moveCard(cardId, payload) {
    return api.post(`/cards/${cardId}/move`, payload).then(getData);
  },
  reorderCards(listId, payload) {
    return api.post(`/lists/${listId}/cards/reorder`, payload).then(getData);
  },
  getAssignees(cardId) {
    return api.get(`/cards/${cardId}/assignees`).then(getData);
  },
  assignUser(cardId, userId) {
    return api.post(`/cards/${cardId}/assignees`, { user_id: userId }).then(getData);
  },
  unassignUser(cardId, userId) {
    return api.delete(`/cards/${cardId}/assignees/${userId}`).then(getData);
  },
};
