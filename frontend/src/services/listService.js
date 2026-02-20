import { api } from "./axios";

const getData = (response) => response.data;

export const listService = {
  createList(boardId, payload) {
    return api.post(`/boards/${boardId}/lists`, payload).then(getData);
  },
  updateList(listId, payload) {
    return api.patch(`/lists/${listId}`, payload).then(getData);
  },
  deleteList(listId) {
    return api.delete(`/lists/${listId}`).then(getData);
  },
  reorderLists(boardId, payload) {
    return api.post(`/boards/${boardId}/lists/reorder`, payload).then(getData);
  },
};
