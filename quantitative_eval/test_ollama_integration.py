#!/usr/bin/env python3
"""
Test Ollama integration for RAG system
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from core.intelligent_rag_system import IntelligentRAGSystem


def test_ollama_rag():
    """Test RAG system with Ollama enabled"""

    print("=" * 80)
    print("Test Intelligent RAG System with Ollama LLM")
    print("=" * 80)
    print()

    # Initialize system with LLM enabled
    print("Initializing RAG system with Ollama...")
    rag = IntelligentRAGSystem(use_llm=True, llm_model="llama3.2")
    print()

    # Test cases
    test_cases = [
        {
            "query": "What metaphor does Romeo use to describe Juliet when he sees her at the window?",
            "expected_type": "Known",
            "description": "Known question (should return passage directly)"
        },
        {
            "query": "How does Tybalt's language and attitude toward Romeo evolve through different acts?",
            "expected_type": "Inferred",
            "description": "Inferred question (should use LLM to synthesize passages)"
        },
        {
            "query": "What would happen if Romeo and Juliet had smartphones?",
            "expected_type": "Out-of-KB",
            "description": "Out-of-KB question (should use LLM general knowledge)"
        }
    ]

    print("=" * 80)
    print("Test Cases")
    print("=" * 80)

    for i, case in enumerate(test_cases, 1):
        print(f"\n【Test {i}】 {case['description']}")
        print(f"Question: {case['query']}")
        print(f"Expected type: {case['expected_type']}")
        print("-" * 80)

        answer, qtype, passages = rag.answer_question(case['query'], debug=True)

        print(f"\nActual type: {qtype}")
        print(f"Match: {'✓' if qtype == case['expected_type'] else '✗'}")
        print()
        print(f"Final Answer:")
        print(f"{answer}")
        print("=" * 80)


if __name__ == "__main__":
    test_ollama_rag()
