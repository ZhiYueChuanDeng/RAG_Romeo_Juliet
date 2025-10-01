#!/usr/bin/env python3
"""
Oracle评估：假设我们已经完美分类了问题类型
用于计算理论性能上限
"""

import os
import pandas as pd
import pytrec_eval
from collections import defaultdict

def oracle_evaluation():
    """
    Oracle评估：对每种问题类型使用最优方法
    - Known: Hybrid 3-Level (DPR+MiniLM)
    - Inferred: FAISS (MiniLM) - 95%准确率
    - Out-of-KB: 不返回结果
    """

    print("=" * 80)
    print("Oracle评估 - 理论性能上限")
    print("=" * 80)

    # 读取数据
    question_types = pd.read_csv("data/question_types.csv")
    qrels_df = pd.read_csv("data/qrels.txt", sep="\t", header=None,
                          names=['qid', 'Q0', 'pid', 'rel'])

    # 读取各方法的runs
    print("\n加载各方法的runs文件...")

    # Hybrid 3-Level的runs
    hybrid_runs = defaultdict(dict)
    with open("target/runs/romeo-juliet-hybrid.txt", 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 6:
                hybrid_runs[parts[0]][parts[2]] = float(parts[4])

    # MiniLM的runs（用于Inferred）
    minilm_runs = defaultdict(dict)
    with open("target/runs/romeo-juliet-faiss.txt", 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 6:
                minilm_runs[parts[0]][parts[2]] = float(parts[4])

    # 构建Oracle runs
    print("\n构建Oracle runs（每种问题类型使用最优方法）...")
    oracle_runs = defaultdict(dict)

    known_count = 0
    inferred_count = 0
    out_of_kb_count = 0

    for _, row in question_types.iterrows():
        qid = row['question_id']
        qtype = row['question_type']

        if qtype == 'Known':
            # Known使用Hybrid 3-Level
            if qid in hybrid_runs:
                oracle_runs[qid] = hybrid_runs[qid]
                known_count += 1
        elif qtype == 'Inferred':
            # Inferred使用MiniLM
            if qid in minilm_runs:
                oracle_runs[qid] = minilm_runs[qid]
                inferred_count += 1
        else:  # Out-of-KB
            # Out-of-KB不返回结果
            out_of_kb_count += 1
            pass

    print(f"  Known问题: {known_count} (使用Hybrid 3-Level)")
    print(f"  Inferred问题: {inferred_count} (使用FAISS MiniLM)")
    print(f"  Out-of-KB问题: {out_of_kb_count} (不返回结果)")

    # 加载qrels
    qrels = defaultdict(dict)
    for _, row in qrels_df.iterrows():
        qrels[row['qid']][row['pid']] = row['rel']

    # 分别评估各类型
    print("\n" + "=" * 80)
    print("Oracle评估结果（理论上限）")
    print("=" * 80)

    results_by_type = {}

    for qtype in ['Known', 'Inferred']:
        type_questions = set(question_types[question_types['question_type'] == qtype]['question_id'])

        # 过滤qrels和runs
        type_qrels = {qid: qrels[qid] for qid in type_questions if qid in qrels}
        type_runs = {qid: oracle_runs[qid] for qid in type_questions if qid in oracle_runs}

        if not type_qrels or not type_runs:
            continue

        # 评估
        evaluator = pytrec_eval.RelevanceEvaluator(type_qrels, {'map', 'ndcg', 'P_4', 'recall_4', 'bpref'})
        results = evaluator.evaluate(type_runs)

        # 计算平均值
        metrics = defaultdict(list)
        for qid, res in results.items():
            for metric, value in res.items():
                metrics[metric].append(value)

        avg_metrics = {
            'map': sum(metrics['map']) / len(metrics['map']) if metrics['map'] else 0,
            'ndcg': sum(metrics['ndcg']) / len(metrics['ndcg']) if metrics['ndcg'] else 0,
            'P_4': sum(metrics['P_4']) / len(metrics['P_4']) if metrics['P_4'] else 0,
            'recall_4': sum(metrics['recall_4']) / len(metrics['recall_4']) if metrics['recall_4'] else 0,
            'bpref': sum(metrics['bpref']) / len(metrics['bpref']) if metrics['bpref'] else 0
        }

        results_by_type[qtype] = avg_metrics

        print(f"\n【{qtype}问题 - Oracle】")
        print(f"  MAP: {avg_metrics['map']:.4f}")
        print(f"  NDCG: {avg_metrics['ndcg']:.4f}")
        print(f"  P@4: {avg_metrics['P_4']:.4f}")
        print(f"  Recall@4: {avg_metrics['recall_4']:.4f}")
        print(f"  BPref: {avg_metrics['bpref']:.4f}")

    # Out-of-KB
    print(f"\n【Out-of-KB问题 - Oracle】")
    print(f"  未回答比例: 100.00% (理论完美)")

    # 与实际方法对比
    print("\n" + "=" * 80)
    print("Oracle vs 实际方法对比")
    print("=" * 80)

    # 读取Hybrid 3-Level的实际评估结果
    print("\n【Known问题】")
    print(f"  Oracle (Hybrid 3-Level): NDCG={results_by_type['Known']['ndcg']:.4f}, P@4={results_by_type['Known']['P_4']:.4f}")
    print(f"  实际 Hybrid 3-Level: NDCG=0.5811, P@4=0.5483")
    print(f"  差距: 基本一致（Oracle已知问题类型，无需路由判断）")

    print("\n【Inferred问题】")
    print(f"  Oracle (MiniLM直接): NDCG={results_by_type['Inferred']['ndcg']:.4f}, P@4={results_by_type['Inferred']['P_4']:.4f}")
    print(f"  实际 Hybrid 3-Level: NDCG=0.4110, P@4=0.4125")
    print(f"  实际 MiniLM (无路由): NDCG=0.9513, P@4=0.9500")
    print(f"  提升: Oracle比Hybrid提升 {(results_by_type['Inferred']['ndcg']/0.4110 - 1)*100:.1f}%")

    print("\n【Out-of-KB问题】")
    print(f"  Oracle: 100% 未回答 (完美识别)")
    print(f"  实际 Hybrid 3-Level: 45% 未回答")
    print(f"  差距: 仍有55%的Out-of-KB问题被误判")

    # 计算整体Oracle性能
    print("\n" + "=" * 80)
    print("整体性能对比")
    print("=" * 80)

    # Oracle整体（加权平均）
    total_questions = known_count + inferred_count + out_of_kb_count
    oracle_overall_ndcg = (
        results_by_type['Known']['ndcg'] * known_count +
        results_by_type['Inferred']['ndcg'] * inferred_count
    ) / (known_count + inferred_count)

    oracle_overall_p4 = (
        results_by_type['Known']['P_4'] * known_count +
        results_by_type['Inferred']['P_4'] * inferred_count
    ) / (known_count + inferred_count)

    print(f"\nOracle（完美分类）:")
    print(f"  整体NDCG: {oracle_overall_ndcg:.4f}")
    print(f"  整体P@4: {oracle_overall_p4:.4f}")
    print(f"  Out-of-KB识别率: 100%")

    print(f"\n实际Hybrid 3-Level（自动分类）:")
    print(f"  整体NDCG: 0.5099")
    print(f"  整体P@4: 0.4794")
    print(f"  Out-of-KB识别率: 45%")

    print(f"\n提升潜力:")
    print(f"  NDCG可提升: {(oracle_overall_ndcg/0.5099 - 1)*100:.1f}%")
    print(f"  P@4可提升: {(oracle_overall_p4/0.4794 - 1)*100:.1f}%")
    print(f"  Out-of-KB识别可提升: {(100/45 - 1)*100:.1f}%")

    print("\n" + "=" * 80)
    print("结论")
    print("=" * 80)
    print("\n如果我们能完美分类问题类型（Known/Inferred/Out-of-KB）：")
    print(f"  - Known问题性能不变（已经用了最优方法）")
    print(f"  - Inferred问题性能大幅提升（从41%到95%）")
    print(f"  - Out-of-KB完美识别（从45%到100%）")
    print(f"\n关键挑战: 如何更准确地自动分类问题类型？")
    print(f"  当前路由准确率估计: ~60-70%")
    print(f"  改进方向: 更智能的问题分类器、更多路由信号")


if __name__ == "__main__":
    if not os.path.exists("data/question_types.csv"):
        print("❌ 请在quantitative_eval目录中运行此脚本")
        exit(1)

    oracle_evaluation()
