"""
Paper Archive - Long-term memory for storing and retrieving papers
"""
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel
from typing import Optional, Dict


class PaperArchive:
    """
    Long-term storage for analyzed papers with semantic search capabilities
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'paper_memory.json')

        print("[Memory] Initializing Long-term Archive...")
        self.db_path = db_path
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        self.memory = self._load_db()

    def _load_db(self):
        """Load existing database or create new one"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save(self, paper_obj):
        """Save a paper to the archive with its embedding"""
        if isinstance(paper_obj, BaseModel):
            data = paper_obj.model_dump()
        else:
            data = paper_obj

        embedding = self.encoder.encode(data['one_liner']).tolist()

        entry = {
            "title": data['title'],
            "summary": data['one_liner'],
            "date": "2024-01-01",
            "embedding": embedding
        }
        self.memory.append(entry)

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(self.memory, f)

        print(f"[Memory] Archived: {data['title']}")

    def retrieve_similar(self, current_summary: str, top_k: int = 1) -> Optional[Dict]:
        """
        Find the most similar paper in history.
        Returns None if no similar paper exists or similarity is too low.
        """
        if not self.memory:
            return None

        query_vec = self.encoder.encode([current_summary])
        hist_vecs = np.array([m['embedding'] for m in self.memory])

        scores = cosine_similarity(query_vec, hist_vecs)[0]
        best_idx = np.argmax(scores)

        if scores[best_idx] < 0.3:
            return None

        return self.memory[best_idx]
