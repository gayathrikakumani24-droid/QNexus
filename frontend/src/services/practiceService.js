import apiClient from './apiClient';

/**
 * Starts a new practice session using existing JEE Main questions from MongoDB.
 */
export const startPracticeSession = async (config) => {
  const payload = {
    subject: config.subject && config.subject !== 'All' ? config.subject : null,
    chapter: config.chapter?.trim() || null,
    concept: config.concept?.trim() || null,
    difficulty: config.difficulty && config.difficulty !== 'All' ? config.difficulty : null,
    year: config.year && config.year !== 'All' ? parseInt(config.year, 10) : null,
    session: config.session && config.session !== 'All' ? config.session : null,
    shift: config.shift && config.shift !== 'All' ? config.shift : null,
    paper_id: config.paper_id?.trim() || null,
    num_questions: config.num_questions ? parseInt(config.num_questions, 10) : 10,
  };

  const response = await apiClient.post('/practice/start', payload);
  return response.data;
};

/**
 * Records an answer selection and review status for a question in a practice session.
 */
export const recordPracticeAnswer = async (sessionId, { questionId, selectedAnswer, timeSpentSeconds, markedForReview }) => {
  const response = await apiClient.post(`/practice/${sessionId}/answer`, {
    question_id: questionId,
    selected_answer: selectedAnswer,
    time_spent_seconds: timeSpentSeconds || 0,
    marked_for_review: !!markedForReview,
  });
  return response.data;
};

/**
 * Submits the practice session and evaluates all answers.
 */
export const submitPracticeSession = async (sessionId) => {
  const response = await apiClient.post(`/practice/${sessionId}/submit`);
  return response.data;
};
