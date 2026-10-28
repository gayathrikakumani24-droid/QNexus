import apiClient from './apiClient';

/**
 * Executes semantic search query with metadata filters against /api/v1/search
 * @param {Object} params
 * @param {string} params.query
 * @param {string} [params.subject]
 * @param {string} [params.chapter]
 * @param {string} [params.concept]
 * @param {string} [params.difficulty]
 * @param {number} [params.year]
 * @param {string} [params.session]
 * @param {string} [params.shift]
 * @param {number} [params.top_k]
 * @returns {Promise<Object>} SearchResponse
 */
export const searchQuestions = async (params) => {
  const payload = {
    query: params.query?.trim() || '',
    subject: params.subject && params.subject !== 'All' ? params.subject : null,
    chapter: params.chapter?.trim() || null,
    concept: params.concept?.trim() || null,
    difficulty: params.difficulty && params.difficulty !== 'All' ? params.difficulty : null,
    year: params.year && params.year !== 'All' ? parseInt(params.year, 10) : null,
    session: params.session && params.session !== 'All' ? params.session : null,
    shift: params.shift && params.shift !== 'All' ? params.shift : null,
    top_k: params.top_k ? parseInt(params.top_k, 10) : 100,
    min_score: params.min_score !== undefined ? params.min_score : 0.05,
  };

  const response = await apiClient.post('/search', payload);
  return response.data;
};
