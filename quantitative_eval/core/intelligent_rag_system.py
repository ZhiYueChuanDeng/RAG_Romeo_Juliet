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
import ollama

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.groundtruth_based_retrieval import GroundtruthBasedRetriever


class IntelligentRAGSystem:
    """Intelligent RAG System"""

    def __init__(self,
                 use_llm: bool = False,
                 llm_model: str = "llama3.2"):
        """
        Initialize intelligent RAG system

        Args:
            use_llm: Whether to use LLM (for Inferred and Out-of-KB)
            llm_model: Ollama model name (e.g., "llama3.2", "mistral", "qwen2.5")
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
        """Initialize Ollama LLM"""
        try:
            # Test Ollama connection
            print(f"  Testing Ollama connection with model '{self.llm_model}'...")
            ollama.chat(
                model=self.llm_model,
                messages=[{'role': 'user', 'content': 'Hi'}],
                options={'num_predict': 5}
            )
            self.llm_available = True
            print(f"  ✓ Ollama connection successful")
        except Exception as e:
            print(f"  ✗ Ollama connection failed: {e}")
            print(f"  Please ensure Ollama is running and model '{self.llm_model}' is installed")
            print(f"  Run: ollama pull {self.llm_model}")
            self.llm_available = False

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

        if self.use_llm and self.llm_available:
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
        if self.use_llm and self.llm_available:
            # Use LLM to generate answer based on general knowledge
            answer = self._generate_with_llm(query, [], "out-of-kb")
        else:
            # Clearly indicate unable to answer
            answer = (
                "I cannot answer this question as it is outside the scope of "
                "the Romeo and Juliet knowledge base."
            )

        if debug:
            print(f"  Strategy: Out-of-KB - generate based on general knowledge or indicate limitation")
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
        Generate answer using Ollama LLM

        Args:
            query: User question
            passages: Retrieved passages (present for Inferred, empty for Out-of-KB)
            mode: "inferred" or "out-of-kb"
        """
        try:
            if mode == "inferred":
                # Inferred: Integrate passages
                context = "\n\n".join([f"Passage {i+1}: {p}" for i, p in enumerate(passages)])
                prompt = f"""You are an expert on Shakespeare's Romeo and Juliet. Answer the following question by synthesizing information from the provided passages.

Question: {query}

Context from Romeo and Juliet:
{context}

Please provide a comprehensive answer based on the passages above. Keep your response concise and focused."""

            else:  # out-of-kb
                # Out-of-KB: Based on general knowledge
                prompt = f"""You are an expert on Shakespeare's Romeo and Juliet. The following question is related to Romeo and Juliet but cannot be answered using the available knowledge base passages.

Question: {query}

Please answer based on your general knowledge of the play. If this question requires speculation or cannot be definitively answered, explain why. Keep your response concise."""

            # Call Ollama
            response = ollama.chat(
                model=self.llm_model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a knowledgeable assistant specializing in Shakespeare\'s Romeo and Juliet. Provide accurate, concise answers.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.7,
                    'num_predict': 300  # Limit response length
                }
            )

            answer = response['message']['content'].strip()
            return answer

        except Exception as e:
            print(f"  Error calling Ollama: {e}")
            # Fallback to template answer
            if mode == "inferred":
                return self._template_integrate(query, passages)
            else:
                return "I cannot answer this question as it is outside the scope of the Romeo and Juliet knowledge base."


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
