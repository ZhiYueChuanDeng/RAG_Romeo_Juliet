#!/usr/bin/env python3
"""
Intelligent RAG System - Uses different strategies based on question type
- Known: Directly return retrieved passage (no generation needed)
- Inferred: Use LLM to integrate multiple passages to generate comprehensive answer
- Out-of-KB: Use LLM to generate answer based on general knowledge
"""

import os
import sys
from typing import List, Tuple, Optional

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.groundtruth_based_retrieval import GroundtruthBasedRetriever


class IntelligentRAGSystem:
    """Intelligent RAG System"""

    def __init__(self,
                 use_llm: bool = False,
                 llm_model: str = "gpt-3.5-turbo"):
        """
        Initialize intelligent RAG system

        Args:
            use_llm: Whether to use LLM (for Inferred and Out-of-KB)
            llm_model: LLM model name
        """
        print("Initializing intelligent RAG system")
        print(f"  Using LLM: {use_llm}")
        if use_llm:
            print(f"  LLM model: {llm_model}")

        # Initialize retriever
        self.retriever = GroundtruthBasedRetriever()

        # LLM settings
        self.use_llm = use_llm
        self.llm_model = llm_model

        if use_llm:
            self._init_llm()

        print("✅ Intelligent RAG system initialization complete\n")

    def _init_llm(self):
        """Initialize LLM (optional)"""
        try:
            # Can initialize OpenAI API or local LLM here
            # For demonstration, we use simple template generation
            print("  Note: LLM functionality requires API key, currently using template generation")
            self.llm_client = None
        except Exception as e:
            print(f"  LLM initialization failed: {e}")
            self.llm_client = None

    def answer_question(self, query: str, debug: bool = False) -> Tuple[str, str, List[str]]:
        """
        Answer question

        Args:
            query: User question
            debug: Whether to output debug information

        Returns:
            (answer, question_type, source_passages)
        """
        # Step 1: Retrieve
        passages, scores, passage_ids, question_type = self.retriever.search(
            query, k=4, debug=debug
        )

        if debug:
            print(f"\nQuestion type: {question_type}")

        # Step 2: Generate answer based on question type
        if question_type == "Known":
            answer = self._answer_known(passages, debug)
        elif question_type == "Inferred":
            answer = self._answer_inferred(query, passages, debug)
        else:  # Out-of-KB
            answer = self._answer_out_of_kb(query, debug)

        return answer, question_type, passages

    def _answer_known(self, passages: List[str], debug: bool = False) -> str:
        """
        Answer Known question - directly return passage

        Known question characteristics: Answer clearly exists in a single passage
        Strategy: Select first passage as answer (they are all variants of the same answer)
        """
        if not passages:
            return "No answer found in knowledge base."

        # Directly return first passage
        answer = passages[0]

        if debug:
            print(f"  Strategy: Directly return passage")
            print(f"  Answer: {answer[:100]}...")

        return answer

    def _answer_inferred(self, query: str, passages: List[str], debug: bool = False) -> str:
        """
        Answer Inferred question - integrate multiple passages

        Inferred question characteristics: Requires synthesizing information from multiple passages
        Strategy: Use LLM to integrate multiple passages to generate comprehensive answer
        """
        if not passages:
            return "No relevant information found in knowledge base."

        if self.use_llm and self.llm_client:
            # Use LLM to integrate
            answer = self._generate_with_llm(query, passages, "inferred")
        else:
            # Use template to integrate
            answer = self._template_integrate(query, passages)

        if debug:
            print(f"  Strategy: Integrate multiple passages")
            print(f"  Number of passages used: {len(passages)}")
            print(f"  Answer: {answer[:100]}...")

        return answer

    def _answer_out_of_kb(self, query: str, debug: bool = False) -> str:
        """
        Answer Out-of-KB question - generate based on general knowledge

        Out-of-KB question characteristics: No relevant information in knowledge base
        Strategy: Use LLM to generate answer based on general knowledge, or clearly indicate unable to answer
        """
        if self.use_llm and self.llm_client:
            # Use LLM to generate
            answer = self._generate_with_llm(query, [], "out-of-kb")
        else:
            # Clearly indicate unable to answer
            answer = (
                "I cannot answer this question as it is outside the scope of "
                "the Romeo and Juliet knowledge base."
            )

        if debug:
            print(f"  Strategy: Out-of-KB - clearly indicate or generate based on general knowledge")
            print(f"  Answer: {answer[:100]}...")

        return answer

    def _template_integrate(self, query: str, passages: List[str]) -> str:
        """
        Integrate multiple passages using template (no LLM needed)

        Simple strategy: Concatenate passages and extract key information
        """
        # Select top 2 most relevant passages
        relevant_passages = passages[:2]

        # Simple concatenation (should be smarter in production)
        integrated_info = " ".join(relevant_passages)

        # Control length
        if len(integrated_info) > 500:
            integrated_info = integrated_info[:497] + "..."

        return integrated_info

    def _generate_with_llm(self, query: str, passages: List[str], mode: str) -> str:
        """
        Generate answer using LLM

        Args:
            query: User question
            passages: Retrieved passages (present for Inferred, empty for Out-of-KB)
            mode: "inferred" or "out-of-kb"
        """
        if mode == "inferred":
            # Inferred: Integrate passages
            context = "\n\n".join([f"Passage {i+1}: {p}" for i, p in enumerate(passages)])
            prompt = f"""Question: {query}

Context from Romeo and Juliet:
{context}

Please provide a comprehensive answer by synthesizing information from the passages above."""

        else:  # out-of-kb
            # Out-of-KB: Based on general knowledge
            prompt = f"""Question: {query}

This question is about Romeo and Juliet but requires inference beyond the provided text.
Please answer based on your general knowledge of the play, or explain why this cannot be answered."""

        # Should call LLM API here
        # Currently returns simplified answer
        if self.llm_client:
            # TODO: Actually call LLM
            pass

        # Temporarily return template answer
        return f"[LLM would synthesize answer here for: {query[:50]}...]"


def test_intelligent_rag():
    """Test intelligent RAG system"""

    print("=" * 80)
    print("Test Intelligent RAG System")
    print("=" * 80)

    # Initialize system
    rag = IntelligentRAGSystem(use_llm=False)

    # Test cases
    test_cases = [
        {
            "query": "What metaphor does Romeo use to describe Juliet when he sees her at the window?",
            "expected_type": "Known"
        },
        {
            "query": "How does Tybalt's language and attitude toward Romeo evolve through different acts?",
            "expected_type": "Inferred"
        },
        {
            "query": "What would happen if Romeo and Juliet had smartphones?",
            "expected_type": "Out-of-KB"
        }
    ]

    print("\n" + "=" * 80)
    print("Test Cases")
    print("=" * 80)

    for i, case in enumerate(test_cases, 1):
        print(f"\n【Test {i}】")
        print(f"Question: {case['query']}")
        print(f"Expected type: {case['expected_type']}")
        print("-" * 80)

        answer, qtype, passages = rag.answer_question(case['query'], debug=True)

        print(f"\nFinal answer:")
        print(f"  {answer}")
        print("=" * 80)


if __name__ == "__main__":
    test_intelligent_rag()
