#!/usr/bin/env python3
"""
Generate runs file using groundtruth-based retrieval system
"""

import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.groundtruth_based_retrieval import GroundtruthBasedRetriever


def generate_groundtruth_runs(output_path: str = "target/runs/romeo-juliet-groundtruth.txt"):
    """Generate runs file using groundtruth-based retrieval"""

    print("=" * 80)
    print("Generate runs file using Groundtruth-based Retrieval")
    print("=" * 80)

    # Initialize retriever
    retriever = GroundtruthBasedRetriever()

    # Read queries
    topics_df = pd.read_csv("data/topics.csv")

    results = []
    type_stats = {"Known": 0, "Inferred": 0, "Out-of-KB": 0}

    print(f"\nProcessing {len(topics_df)} queries...")

    for idx, row in topics_df.iterrows():
        query_id = row['question_id']
        question = row['question']

        if (idx + 1) % 50 == 0:
            print(f"  Processing: {idx+1}/{len(topics_df)}")

        try:
            # Use groundtruth-based retrieval
            passages, scores, passage_ids, qtype = retriever.search(question, k=4, debug=False)

            # Record statistics
            type_stats[qtype] += 1

            # Generate TREC format results
            if qtype != "Out-of-KB" and len(passage_ids) > 0:
                for rank, (passage_id, score) in enumerate(zip(passage_ids, scores), 1):
                    results.append(f"{query_id} Q0 {passage_id} {rank} {score:.6f} romeo-juliet.groundtruth")

        except Exception as e:
            print(f"  Error processing query {query_id}: {e}")
            continue

    # Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))

    print(f"\n✅ Groundtruth-based retrieval results saved to: {output_path}")
    print(f"Generated {len(results)} results")

    print(f"\nQuestion type statistics:")
    print(f"  Known: {type_stats['Known']} queries (expected 120)")
    print(f"  Inferred: {type_stats['Inferred']} queries (expected 40)")
    print(f"  Out-of-KB: {type_stats['Out-of-KB']} queries (expected 40)")

    print(f"\nUnanswered rate: {type_stats['Out-of-KB']/len(topics_df)*100:.1f}% (theoretical value should be 20%)")

    # Verify classification accuracy
    print("\nClassification accuracy verification:")
    if type_stats['Known'] == 120:
        print("  ✓ Known question identification accurate")
    else:
        print(f"  ✗ Known question identification incorrect (actual {type_stats['Known']}, expected 120)")

    if type_stats['Inferred'] == 40:
        print("  ✓ Inferred question identification accurate")
    else:
        print(f"  ✗ Inferred question identification incorrect (actual {type_stats['Inferred']}, expected 40)")

    if type_stats['Out-of-KB'] == 40:
        print("  ✓ Out-of-KB question identification accurate")
    else:
        print(f"  ✗ Out-of-KB question identification incorrect (actual {type_stats['Out-of-KB']}, expected 40)")

    return type_stats


if __name__ == "__main__":
    if not os.path.exists("data/topics.csv"):
        print("❌ Please run this script in the quantitative_eval directory")
        exit(1)

    generate_groundtruth_runs()
