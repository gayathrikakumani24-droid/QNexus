import apiClient from './apiClient';

/**
 * Retrieves the knowledge graph representation for a specific concept.
 * Returns: concept, chapter, subject, related_questions, similar_concepts, prerequisites.
 */
export const getConceptKnowledge = async (concept) => {
  const encodedConcept = encodeURIComponent(concept);
  const response = await apiClient.get(`/knowledge/concept/${encodedConcept}`);
  return response.data;
};

/**
 * Retrieves the complete Subject -> Chapter -> Concept hierarchy.
 */
export const getSyllabusHierarchy = async () => {
  const response = await apiClient.get('/knowledge/hierarchy');
  return response.data;
};
