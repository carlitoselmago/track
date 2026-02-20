import { api } from "./axios";

const getData = (response) => response.data;

export const checklistService = {
  createChecklist(cardId, payload) {
    return api.post(`/cards/${cardId}/checklists`, payload).then(getData);
  },
  updateChecklist(checklistId, payload) {
    return api.patch(`/checklists/${checklistId}`, payload).then(getData);
  },
  deleteChecklist(checklistId) {
    return api.delete(`/checklists/${checklistId}`).then(getData);
  },
  createChecklistItem(checklistId, payload) {
    return api.post(`/checklists/${checklistId}/items`, payload).then(getData);
  },
  updateChecklistItem(itemId, payload) {
    return api.patch(`/checklist-items/${itemId}`, payload).then(getData);
  },
  deleteChecklistItem(itemId) {
    return api.delete(`/checklist-items/${itemId}`).then(getData);
  },
};
