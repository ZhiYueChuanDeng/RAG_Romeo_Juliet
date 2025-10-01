#!/usr/bin/env python3
"""
Groundtruth.csv based retrieval system
First match question to find topic, then retrieve answer from groundtruth based on topic
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class GroundtruthBasedRetriever:
    """Groundtruth.csv based retriever"""

    def __init__(self,
                 topics_path: str = "data/topics.csv",
                 groundtruth_path: str = "data/groundtruth.csv",
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize retriever

        Args:
            topics_path: Path to topics.csv file
            groundtruth_path: Path to groundtruth.csv file
            model_name: Embedding model for question matching
        """
        print("Initializing Groundtruth-based retriever")

        # Load data
        print(f"  Loading topics: {topics_path}")
        self.topics_df = pd.read_csv(topics_path)

        print(f"  Loading groundtruth: {groundtruth_path}")
        self.groundtruth_df = pd.read_csv(groundtruth_path)

        # Load embedding model for question matching
        print(f"  Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

        # Build question index
        print("  Building question index...")
        self._build_question_index()

        print("✅ Initialization complete\n")

    def _build_question_index(self):
        """Build question embedding index for fast matching"""
        # Extract all questions
        self.questions = self.topics_df['question'].tolist()
        self.question_ids = self.topics_df['question_id'].tolist()
        self.topic_ids = self.topics_df['topic_id'].tolist()

        # Generate embeddings
        print(f"    Generating embeddings for {len(self.questions)} questions...")
        self.question_embeddings = self.model.encode(
            self.questions,
            convert_to_numpy=True,
            show_progress_bar=True
        )

    def find_matching_topic(self, query: str, top_k: int = 1) -> Tuple[str, str, float]:
        """
        Find the most matching topic for query

        Args:
            query: User input question
            top_k: Return top-k matches

        Returns:
            (topic_id, question_id, similarity_score)
        """
        # Generate embedding for query
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]

        # Calculate similarity
        similarities = np.dot(self.question_embeddings, query_embedding)

        # Find the best matches
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append((
                self.topic_ids[idx],
                self.question_ids[idx],
                float(similarities[idx])
            ))

        return results[0] if top_k == 1 else results

    def search(self, query: str, k: int = 4, debug: bool = False) -> Tuple[List[str], List[float], List[str], str]:
        """
        Retrieval process:
        1. Find the most matching topic
        2. Retrieve passages for that topic from groundtruth
        3. Return results and annotate question type

        Args:
            query: User question
            k: Number of passages to return
            debug: Whether to output debug information

        Returns:
            (passages, scores, passage_ids, question_type)
        """
        # Step 1: Find the most matching topic
        topic_id, question_id, similarity = self.find_matching_topic(query)

        if debug:
            print(f"  Matched topic: {topic_id}")
            print(f"  Matched question_id: {question_id}")
            print(f"  Similarity: {similarity:.4f}")

        # Step 2: Find passages for this topic from groundtruth
        topic_rows = self.groundtruth_df[self.groundtruth_df['topic_id'] == topic_id]

        if len(topic_rows) == 0:
            # Not in groundtruth → Out-of-KB
            if debug:
                print(f"  ✗ Topic not in groundtruth → Out-of-KB")
            return [], [], [], "Out-of-KB"

        # Step 3: Get passages and determine type
        relevance = topic_rows['relevance_judgment'].iloc[0]

        if relevance == 2:
            question_type = "Known"
        elif relevance == 1:
            question_type = "Inferred"
        else:
            question_type = "Unknown"

        # Get all passages (take first k)
        passages = topic_rows['passage'].tolist()[:k]
        passage_ids = topic_rows['passage_id'].tolist()[:k]

        # Set all scores to 1.0 since we're using direct groundtruth matching
        scores = [1.0] * len(passages)

        if debug:
            print(f"  ✓ Question type: {question_type}")
            print(f"  Returning {len(passages)} passages")

        return passages, scores, passage_ids, question_type


def test_groundtruth_retrieval():
    """Test groundtruth-based retrieval system"""

    print("=" * 80)
    print("Test Groundtruth-based Retrieval System")
    print("=" * 80)

    retriever = GroundtruthBasedRetriever()

    # Test cases
    test_cases = [
        {
            "query": "What metaphor does Romeo use to describe Juliet when he sees her at the window?",
            "expected_type": "Known",
            "description": "Known question test"
        },
        {
            "query": "How does Tybalt's language and attitude toward Romeo evolve through different acts?",
            "expected_type": "Inferred",
            "description": "Inferred question test"
        },
        {
            "query": "What would happen if Romeo and Juliet had smartphones?",
            "expected_type": "Out-of-KB",
            "description": "Out-of-KB question test"
        }
    ]

    print("\n" + "=" * 80)
    print("Test Cases")
    print("=" * 80)

    for i, case in enumerate(test_cases, 1):
        print(f"\n【Test {i}】{case['description']}")
        print(f"Question: {case['query'][:80]}...")
        print(f"Expected type: {case['expected_type']}")
        print("-" * 80)

        passages, scores, pids, qtype = retriever.search(case['query'], k=4, debug=True)

        print(f"\nActual type: {qtype}")
        print(f"Match: {'✓' if qtype == case['expected_type'] else '✗'}")

        if qtype != "Out-of-KB":
            print(f"Returned results:")
            for j, (pid, passage) in enumerate(zip(pids, passages), 1):
                print(f"  {j}. {pid}: {passage[:100]}...")

        print("=" * 80)


if __name__ == "__main__":
    test_groundtruth_retrieval()
