import { api } from "./axios";

const getData = (response) => response.data;

export const imageService = {
  uploadCardImage(cardId, file) {
    const formData = new FormData();
    formData.append("file", file);
    return api
      .post(`/cards/${cardId}/images`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then(getData);
  },
  getCardImages(cardId) {
    return api.get(`/cards/${cardId}/images`).then(getData);
  },
  deleteImage(imageId) {
    return api.delete(`/images/${imageId}`).then(getData);
  },
  setCardCover(cardId, imageId) {
    return api.post(`/cards/${cardId}/cover/${imageId}`).then(getData);
  },
  getImageContentUrl(imageId) {
    return `${api.defaults.baseURL}/images/${imageId}/content`;
  },
};
