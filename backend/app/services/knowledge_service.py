import logging
from typing import List, Dict, Any, Optional
from pymongo.database import Database
from app.core.database import get_mongo_db
from app.repositories.knowledge_repository import BaseKnowledgeRepository, MongoKnowledgeRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.knowledge_schema import (
    ConceptKnowledgeResponse,
    KnowledgeHierarchyResponse,
    SubjectHierarchyNode,
    ChapterHierarchyNode
)
from app.schemas.question_schema import QuestionResponse

logger = logging.getLogger("qnexus.services.knowledge")

# Curated Syllabus Prerequisite Map (JEE Main Core Concepts)
SYLLABUS_PREREQUISITES: Dict[str, List[str]] = {
    # Physics
    "torque": ["Moment of Inertia", "Cross Product", "Newton's Laws of Motion", "Equilibrium of Rigid Bodies"],
    "moment of inertia": ["Center of Mass", "Integration", "Rigid Body Kinematics"],
    "angular momentum": ["Torque", "Moment of Inertia", "Conservation of Linear Momentum"],
    "rolling motion": ["Torque", "Friction", "Rotational Kinetic Energy", "Work-Energy Theorem"],
    "carnot engine": ["Second Law of Thermodynamics", "First Law of Thermodynamics", "Isothermal & Adiabatic Processes"],
    "first law of thermodynamics": ["Work Done in Thermodynamic Processes", "Internal Energy", "Heat Capacity"],
    "electric potential": ["Coulomb's Law", "Electrostatic Force", "Work-Energy Theorem", "Electric Field"],
    "capacitance": ["Electric Potential", "Electric Field", "Dielectrics", "Gauss's Law"],
    "electromagnetic induction": ["Magnetic Flux", "Faraday's Law", "Lenz's Law", "Lorentz Force"],
    "simple harmonic motion": ["Hooke's Law", "Restoring Force", "Kinematics", "Energy Conservation"],
    "wave optics": ["Huygens' Principle", "Interference", "Superposition Principle", "Diffraction"],
    "projectile motion": ["Kinematic Equations", "Resolution of Vectors", "Gravity"],

    # Chemistry
    "hybridization": ["VSEPR Theory", "Atomic Orbitals", "Electronic Configuration", "Valence Bond Theory"],
    "chemical bonding": ["Octet Rule", "Electronegativity", "Periodic Trends", "Lewis Structures"],
    "chemical equilibrium": ["Rate of Reaction", "Le Chatelier's Principle", "Law of Mass Action"],
    "electrochemistry": ["Redox Reactions", "Oxidation Numbers", "Standard Electrode Potential", "Nernst Equation"],
    "coordination compounds": ["Crystal Field Theory", "Ligands", "d-Block Elements", "Isomerism"],
    "aldehydes and ketones": ["Nucleophilic Addition", "Alcohols", "Oxidation & Reduction", "Carbonyl Group"],
    "thermodynamics (chemistry)": ["Enthalpy", "Entropy", "Gibbs Free Energy", "Hess's Law"],
    "solutions and colligative properties": ["Raoult's Law", "Molarity & Molality", "Vapour Pressure"],

    # Mathematics
    "definite integrals": ["Indefinite Integration", "Fundamental Theorem of Calculus", "Substitution Method", "Limits"],
    "differential equations": ["Indefinite Integration", "Derivatives", "Variable Separation Method"],
    "matrices and determinants": ["Cramer's Rule", "Linear Equations", "Matrix Multiplication", "Inverse of Matrix"],
    "vectors and 3d geometry": ["Dot Product", "Cross Product", "Direction Cosines", "Plane Equations"],
    "probability": ["Bayes' Theorem", "Conditional Probability", "Permutations & Combinations"],
    "continuity and differentiability": ["Limits", "Derivatives", "L'Hopital's Rule", "Functions"],
    "complex numbers": ["Argand Plane", "De Moivre's Theorem", "Modulus & Argument", "Quadratic Equations"],
    "parabola": ["Conic Sections", "Distance Formula", "Coordinate Geometry", "Focus and Directrix"]
}

class KnowledgeService:
    def __init__(
        self,
        db: Optional[Database] = None,
        knowledge_repo: Optional[BaseKnowledgeRepository] = None,
        question_repo: Optional[QuestionRepository] = None
    ):
        self.db = db if db is not None else get_mongo_db()
        self.repo = knowledge_repo or MongoKnowledgeRepository(self.db)
        self.question_repo = question_repo or QuestionRepository(self.db)

    def get_concept_knowledge(self, concept: str) -> ConceptKnowledgeResponse:
        """
        Retrieves graph relationship view for a concept:
        - Parent Chapter & Subject
        - Related questions testing this concept
        - Co-occurring/Similar concepts in the chapter
        - Foundational prerequisite concepts
        """
        clean_concept = concept.strip()
        concept_lower = clean_concept.lower()

        # 1. Fetch concept metadata
        meta = self.repo.get_concept_metadata(clean_concept)
        if not meta:
            # If concept not directly found in DB metadata, provide default contextual structure
            chapter = "General"
            subject = "General"
        else:
            chapter = meta.get("chapter", "General")
            subject = meta.get("subject", "General")

        # 2. Fetch related questions from MongoDB
        raw_questions = self.repo.get_related_questions(clean_concept, limit=15)
        related_questions: List[QuestionResponse] = []
        for doc in raw_questions:
            try:
                related_questions.append(QuestionResponse(**doc))
            except Exception as e:
                logger.warning(f"Failed to parse question response in knowledge service: {e}")

        # 3. Find similar/sibling concepts in the same chapter
        similar_concepts = self.repo.get_sibling_concepts_in_chapter(
            chapter=chapter,
            exclude_concept=clean_concept
        )

        # 4. Determine prerequisites
        # First check standard syllabus prerequisite map
        prerequisites = SYLLABUS_PREREQUISITES.get(concept_lower)

        if not prerequisites:
            # Check for partial key matches in prerequisite dictionary
            for key, prereqs in SYLLABUS_PREREQUISITES.items():
                if key in concept_lower or concept_lower in key:
                    prerequisites = prereqs
                    break

        if not prerequisites:
            # Fallback: select other foundational concepts in the chapter
            prerequisites = [c for c in similar_concepts[:3]] if similar_concepts else ["Fundamental Principles of " + chapter]

        return ConceptKnowledgeResponse(
            concept=meta.get("concept", clean_concept) if meta else clean_concept,
            chapter=chapter,
            subject=subject,
            related_questions=related_questions,
            similar_concepts=similar_concepts[:6],
            prerequisites=prerequisites
        )

    def get_syllabus_hierarchy(self) -> KnowledgeHierarchyResponse:
        """
        Retrieves the complete Subject -> Chapter -> Concept hierarchy.
        Combines canonical complete JEE Main syllabus taxonomy with dynamic MongoDB question aggregations.
        """
        import os
        import json

        # 1. Load canonical JEE Main syllabus taxonomy
        candidate_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jee_main_syllabus.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "jee_main_syllabus.json"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "jee_main_syllabus.json"),
        ]
        base_taxonomy: Dict[str, Dict[str, List[str]]] = {}
        for path in candidate_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        raw_tax = json.load(f)
                        for subj, ch_list in raw_tax.items():
                            base_taxonomy[subj] = {item["chapter"]: list(item.get("concepts", [])) for item in ch_list}
                    if base_taxonomy:
                        break
                except Exception as e:
                    logger.warning(f"Could not load jee_main_syllabus.json from {path}: {e}")

        # 2. Merge dynamic DB tree if available
        try:
            raw_tree = self.repo.get_hierarchy_tree()
            for subj_doc in raw_tree:
                subj_name = subj_doc.get("_id") or "Unknown"
                if subj_name not in base_taxonomy:
                    base_taxonomy[subj_name] = {}
                for ch in subj_doc.get("chapters", []):
                    ch_name = ch.get("chapter") or "General"
                    existing = base_taxonomy[subj_name].setdefault(ch_name, [])
                    for c in ch.get("concepts", []):
                        if c and c.strip() and c not in existing:
                            existing.append(c.strip())
        except Exception as e:
            logger.warning(f"Could not aggregate dynamic hierarchy from DB: {e}")

        # 3. Build response nodes
        hierarchy: List[SubjectHierarchyNode] = []
        for subj_name, chapters_dict in base_taxonomy.items():
            chapter_nodes = [
                ChapterHierarchyNode(chapter=ch, concepts=concepts)
                for ch, concepts in chapters_dict.items()
            ]
            hierarchy.append(
                SubjectHierarchyNode(subject=subj_name, chapters=chapter_nodes)
            )

        return KnowledgeHierarchyResponse(hierarchy=hierarchy)
