import { fetchApi } from './client';

export const feedbackApi = {
  submitFeedback: async (feedbackData) => {
    return fetchApi('/feedback', {
      method: 'POST',
      body: JSON.stringify(feedbackData),
    });
  },
  
  getStats: async () => {
    return fetchApi('/feedback/stats');
  }
};
