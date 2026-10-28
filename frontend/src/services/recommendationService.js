import apiClient from './apiClient';

/**
 * Retrieves personalized, explainable question recommendations based on actual student performance.
 */
export const getRecommendations = async (params = {}) => {
  const cleanParams = {};
  if (params.userId) cleanParams.user_id = params.userId;
  if (params.subject && params.subject !== 'All') cleanParams.subject = params.subject;
  if (params.limit) cleanParams.limit = params.limit;

  const response = await apiClient.get('/recommendations', { params: cleanParams });
  return response.data;
};
