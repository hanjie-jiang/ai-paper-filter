"""
Curator Module - Relevance matching between papers and user preferences
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from brain import ResearchProfile


class Curator:
    """Matchmaker module for calculating paper relevance"""

    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

    def calculate_relevance(self, paper_summary: str, profile: ResearchProfile) -> float:
        """
        Calculate semantic similarity between paper and user interests.
        Returns a score between 0 and 1.
        """
        paper_vec = self.encoder.encode([paper_summary])
        interest_vecs = self.encoder.encode(profile.interests)
        user_concept_vec = np.mean(interest_vecs, axis=0).reshape(1, -1)

        similarity = cosine_similarity(paper_vec, user_concept_vec)[0][0]

        for bad_word in profile.negative_keywords:
            if bad_word.lower() in paper_summary.lower():
                return 0.0

        return float(similarity)
