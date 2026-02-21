import { api } from "./axios";

const getData = (response) => response.data;

export const boardService = {
  getBoards() {
    return api.get("/boards").then(getData);
  },
  getBoard(boardId) {
    return api.get(`/boards/${boardId}`).then(getData);
  },
  createBoard(payload) {
    return api.post("/boards", payload).then(getData);
  },
  updateBoard(boardId, payload) {
    return api.patch(`/boards/${boardId}`, payload).then(getData);
  },
  deleteBoard(boardId) {
    return api.delete(`/boards/${boardId}`).then(getData);
  },
  getBoardMembers(boardId) {
    return api.get(`/boards/${boardId}/members`).then(getData);
  },
  addBoardMember(boardId, userId, role = "member") {
    return api.post(`/boards/${boardId}/members`, { user_id: userId, role }).then(getData);
  },
  removeBoardMember(boardId, userId) {
    return api.delete(`/boards/${boardId}/members/${userId}`).then(getData);
  },
  getBoardCalendar(boardId, month) {
    return api
      .get(`/boards/${boardId}/calendar`, { params: { month } })
      .then(getData);
  },
};
