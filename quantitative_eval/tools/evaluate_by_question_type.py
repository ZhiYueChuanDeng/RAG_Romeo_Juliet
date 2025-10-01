#!/usr/bin/env python3
"""
Evaluate Romeo & Juliet RAG system by question type
Mimics the evaluation approach from the original paper
"""

import os
import pandas as pd
import pytrec_eval
from collections import defaultdict

def load_qrels(qrels_file: str):
    """Load qrels file"""
    qrels = defaultdict(dict)
    with open(qrels_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                query_id = parts[0]
                doc_id = parts[2]
                relevance = int(parts[3])
                qrels[query_id][doc_id] = relevance
    return dict(qrels)

def load_runs(runs_file: str):
    """Load runs file"""
    runs = defaultdict(dict)
    with open(runs_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 6:
                query_id = parts[0]
                doc_id = parts[2]
                score = float(parts[4])
                runs[query_id][doc_id] = score
    return dict(runs)

def evaluate_by_type(qrels_file: str, runs_file: str, question_types_file: str, method_name: str):
    """Evaluate by question type"""

    print(f"\n{'='*70}")
    print(f"Evaluation method: {method_name}")
    print(f"{'='*70}")

    # Load data
    qrels = load_qrels(qrels_file)
    runs = load_runs(runs_file)
    question_types_df = pd.read_csv(question_types_file)

    # Group by type
    type_groups = {
        'Known': set(question_types_df[question_types_df['question_type'] == 'Known']['question_id']),
        'Inferred': set(question_types_df[question_types_df['question_type'] == 'Inferred']['question_id']),
        'Out-of-KB': set(question_types_df[question_types_df['question_type'] == 'Out-of-KB']['question_id'])
    }

    results = {}

    for qtype, question_ids in type_groups.items():
        print(f"\n【{qtype} Question Evaluation】")
        print(f"Number of questions: {len(question_ids)}")

        if qtype == 'Out-of-KB':
            # Out-of-KB questions have no qrels, calculate unanswered ratio
            answered_count = sum(1 for qid in question_ids if qid in runs)
            unanswered_pct = (len(question_ids) - answered_count) / len(question_ids) * 100
            print(f"Unanswered question ratio: {unanswered_pct:.2f}%")
            results[qtype] = {
                'unanswered_pct': unanswered_pct,
                'total_questions': len(question_ids)
            }
            continue

        # Filter qrels and runs, keep only current type questions
        filtered_qrels = {qid: qrels[qid] for qid in question_ids if qid in qrels}
        filtered_runs = {qid: runs[qid] for qid in question_ids if qid in runs}

        if not filtered_qrels:
            print(f"⚠️  No qrels data")
            continue

        # Create evaluator
        evaluator = pytrec_eval.RelevanceEvaluator(
            filtered_qrels,
            {'map', 'ndcg', 'P_4', 'recall_4', 'bpref'}
        )

        # Run evaluation
        eval_results = evaluator.evaluate(filtered_runs)

        # Calculate averages
        metrics_avg = defaultdict(list)
        for query_id, query_results in eval_results.items():
            for metric, value in query_results.items():
                metrics_avg[metric].append(value)

        # Display results
        print(f"\nRetrieval metrics (average):")
        for metric in ['map', 'ndcg', 'P_4', 'recall_4', 'bpref']:
            if metric in metrics_avg:
                avg_value = sum(metrics_avg[metric]) / len(metrics_avg[metric])
                print(f"  {metric.upper()}: {avg_value:.4f}")

        results[qtype] = {
            'map': sum(metrics_avg['map']) / len(metrics_avg['map']),
            'ndcg': sum(metrics_avg['ndcg']) / len(metrics_avg['ndcg']),
            'P_4': sum(metrics_avg['P_4']) / len(metrics_avg['P_4']),
            'recall_4': sum(metrics_avg['recall_4']) / len(metrics_avg['recall_4']),
            'bpref': sum(metrics_avg['bpref']) / len(metrics_avg['bpref']),
            'total_questions': len(filtered_qrels)
        }

    return results

def generate_comparison_table(all_results: dict):
    """Generate comparison table"""

    print(f"\n{'='*70}")
    print("All methods comparison (by question type)")
    print(f"{'='*70}")

    # Known question comparison
    print(f"\n【Known Questions】")
    print(f"{'Method':<30} {'NDCG':>8} {'MAP':>8} {'P@4':>8} {'Recall@4':>8} {'BPref':>8}")
    print("-" * 70)
    for method, results in all_results.items():
        if 'Known' in results:
            r = results['Known']
            print(f"{method:<30} {r['ndcg']:>8.4f} {r['map']:>8.4f} {r['P_4']:>8.4f} "
                  f"{r['recall_4']:>8.4f} {r['bpref']:>8.4f}")

    # Inferred question comparison
    print(f"\n【Inferred Questions】")
    print(f"{'Method':<30} {'NDCG':>8} {'MAP':>8} {'P@4':>8} {'Recall@4':>8} {'BPref':>8}")
    print("-" * 70)
    for method, results in all_results.items():
        if 'Inferred' in results:
            r = results['Inferred']
            print(f"{method:<30} {r['ndcg']:>8.4f} {r['map']:>8.4f} {r['P_4']:>8.4f} "
                  f"{r['recall_4']:>8.4f} {r['bpref']:>8.4f}")

    # Out-of-KB question comparison
    print(f"\n【Out-of-KB Questions】")
    print(f"{'Method':<30} {'Unanswered Ratio':>12}")
    print("-" * 70)
    for method, results in all_results.items():
        if 'Out-of-KB' in results:
            r = results['Out-of-KB']
            print(f"{method:<30} {r['unanswered_pct']:>11.2f}%")

    # Save as CSV
    rows = []
    for method, results in all_results.items():
        for qtype in ['Known', 'Inferred', 'Out-of-KB']:
            if qtype in results:
                row = {'method': method, 'question_type': qtype}
                row.update(results[qtype])
                rows.append(row)

    df = pd.DataFrame(rows)
    output_file = "target/summaries/evaluation_by_question_type.csv"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"\n✅ Detailed results saved to: {output_file}")

def main():
    """Main function"""

    # Ensure running in correct directory
    if not os.path.exists("data/qrels.txt"):
        print("❌ Please run this script in the quantitative_eval directory")
        return

    # Ensure question type classification has been generated
    if not os.path.exists("data/question_types.csv"):
        print("❌ Please run analyze_question_types.py first to generate question classification")
        return

    qrels_file = "data/qrels.txt"
    question_types_file = "data/question_types.csv"

    # Configure methods to evaluate
    runs_configs = [
        {
            "runs_file": "target/runs/romeo-juliet-groundtruth.txt",
            "method_name": "Groundtruth-Based (MiniLM)"
        },
        {
            "runs_file": "target/runs/romeo-juliet-hybrid.txt",
            "method_name": "Hybrid 3-Level (DPR+MiniLM)"
        },
        {
            "runs_file": "target/runs/romeo-juliet-hierarchical.txt",
            "method_name": "3-Level (DPR only)"
        },
        {
            "runs_file": "target/runs/romeo-juliet-dpr.txt",
            "method_name": "FAISS (DPR)"
        },
        {
            "runs_file": "target/runs/romeo-juliet-faiss.txt",
            "method_name": "FAISS (MiniLM)"
        },
        {
            "runs_file": "target/runs/romeo-juliet-bm25.txt",
            "method_name": "BM25"
        }
    ]

    all_results = {}

    for config in runs_configs:
        runs_file = config["runs_file"]
        method_name = config["method_name"]

        if not os.path.exists(runs_file):
            print(f"⚠️  runs file does not exist: {runs_file}")
            continue

        results = evaluate_by_type(qrels_file, runs_file, question_types_file, method_name)
        all_results[method_name] = results

    # Generate comparison table
    if all_results:
        generate_comparison_table(all_results)

if __name__ == "__main__":
    main()
