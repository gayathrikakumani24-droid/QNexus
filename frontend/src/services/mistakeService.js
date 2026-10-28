import apiClient from './apiClient';

/**
 * Saves or updates a mistake in the student's notebook.
 */
export const saveMistake = async ({
  questionId,
  userId = 'default_user',
  userAnswer = null,
  correctAnswer = null,
  mistakeTag = 'Conceptual Gap',
  userNotes = '',
  reviewStatus = 'Needs Review',
  subject = null,
  chapter = null,
  concept = null,
}) => {
  const response = await apiClient.post('/mistakes', {
    question_id: questionId,
    user_id: userId,
    user_answer: userAnswer,
    correct_answer: correctAnswer,
    mistake_tag: mistakeTag,
    user_notes: userNotes,
    review_status: reviewStatus,
    subject,
    chapter,
    concept,
  });
  return response.data;
};

/**
 * Fetches mistake notebook entries with optional filtering.
 */
export const listMistakes = async (params = {}) => {
  const cleanParams = {};
  if (params.subject && params.subject !== 'All') cleanParams.subject = params.subject;
  if (params.chapter && params.chapter !== 'All') cleanParams.chapter = params.chapter;
  if (params.mistakeTag && params.mistakeTag !== 'All') cleanParams.mistake_tag = params.mistakeTag;
  if (params.reviewStatus && params.reviewStatus !== 'All') cleanParams.review_status = params.reviewStatus;
  if (params.userId) cleanParams.user_id = params.userId;
  if (params.limit) cleanParams.limit = params.limit;
  if (params.offset) cleanParams.offset = params.offset;

  const response = await apiClient.get('/mistakes', { params: cleanParams });
  return response.data;
};

/**
 * Updates a mistake's tag, notes, or review status.
 */
export const updateMistake = async (mistakeId, updates) => {
  const response = await apiClient.patch(`/mistakes/${mistakeId}`, updates);
  return response.data;
};

/**
 * Deletes a mistake from the notebook.
 */
export const deleteMistake = async (mistakeId) => {
  const response = await apiClient.delete(`/mistakes/${mistakeId}`);
  return response.data;
};
