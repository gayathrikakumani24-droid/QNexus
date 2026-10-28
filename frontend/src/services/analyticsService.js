import apiClient from './apiClient';

/**
 * Retrieves overall user practice summary analytics.
 */
export const getAnalyticsSummary = async () => {
  const response = await apiClient.get('/analytics/summary');
  return response.data;
};

/**
 * Retrieves subject-level accuracy and attempt statistics.
 */
export const getSubjectAnalytics = async () => {
  const response = await apiClient.get('/analytics/subjects');
  return response.data;
};

/**
 * Retrieves chapter-level accuracy and attempt statistics.
 */
export const getChapterAnalytics = async (subject = null) => {
  const response = await apiClient.get('/analytics/chapters', {
    params: subject && subject !== 'All' ? { subject } : {},
  });
  return response.data;
};

/**
 * Retrieves concept-level accuracy and attempt statistics.
 */
export const getConceptAnalytics = async (subject = null, chapter = null) => {
  const params = {};
  if (subject && subject !== 'All') params.subject = subject;
  if (chapter && chapter !== 'All') params.chapter = chapter;

  const response = await apiClient.get('/analytics/concepts', { params });
  return response.data;
};

/**
 * Retrieves rule-based weakness analysis based on minimum attempts and accuracy threshold.
 */
export const getWeaknesses = async (minAttempts = 3, weakThreshold = 60.0, subject = null) => {
  const params = {
    min_attempts: minAttempts,
    weak_threshold: weakThreshold,
  };
  if (subject && subject !== 'All') params.subject = subject;

  const response = await apiClient.get('/analytics/weaknesses', { params });
  return response.data;
};
