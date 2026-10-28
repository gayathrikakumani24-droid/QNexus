import apiClient from './apiClient';

/**
 * Generates an in-depth AI step-by-step explanation for a question.
 */
export const explainQuestion = async (questionId, userAttempt = null) => {
  const response = await apiClient.post('/ai/explain', {
    question_id: questionId,
    user_attempt: userAttempt,
  });
  return response.data;
};

/**
 * Retrieves a progressive hint (level 1, 2, or 3) for a question.
 */
export const getQuestionHint = async (questionId, hintLevel = 1) => {
  const response = await apiClient.post('/ai/hint', {
    question_id: questionId,
    hint_level: hintLevel,
  });
  return response.data;
};

/**
 * Retrieves semantically similar previous year questions.
 */
export const getSimilarQuestions = async (questionId, topK = 5, minScore = 0.05) => {
  const response = await apiClient.get(`/questions/${questionId}/similar`, {
    params: { top_k: topK, min_score: minScore },
  });
  return response.data;
};

/**
 * Fetches question document by ID.
 */
export const getQuestionById = async (questionId) => {
  const response = await apiClient.get(`/questions/${questionId}`);
  return response.data;
};
