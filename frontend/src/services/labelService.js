import { api } from "./axios";

const getData = (response) => response.data;

export const labelService = {
  getBoardLabels(boardId) {
    return api.get(`/boards/${boardId}/labels`).then(getData);
  },
  createLabel(boardId, payload) {
    return api.post(`/boards/${boardId}/labels`, payload).then(getData);
  },
  updateLabel(labelId, payload) {
    return api.patch(`/labels/${labelId}`, payload).then(getData);
  },
  deleteLabel(labelId) {
    return api.delete(`/labels/${labelId}`).then(getData);
  },
  assignLabel(cardId, labelId) {
    return api.post(`/cards/${cardId}/labels/${labelId}`).then(getData);
  },
  unassignLabel(cardId, labelId) {
    return api.delete(`/cards/${cardId}/labels/${labelId}`).then(getData);
  },
};
