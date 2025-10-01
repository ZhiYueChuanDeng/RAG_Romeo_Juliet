#!/usr/bin/env python3
"""
使用DPR模型生成runs文件
"""

import os
import sys
import pandas as pd

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.dpr_faiss_retrieval import DPRFAISSRetriever

def generate_dpr_run(output_path: str = "target/runs/romeo-juliet-dpr.txt"):
    """使用DPR生成runs文件"""
    print("=== 生成DPR检索结果 ===")

    # 初始化DPR检索器
    retriever = DPRFAISSRetriever()

    # 加载索引
    print("加载DPR索引...")
    retriever.load_index("target/indexes/faiss_dpr")

    # 读取查询
    topics_df = pd.read_csv("data/topics.csv")

    results = []

    for idx, row in topics_df.iterrows():
        query_id = row['question_id']
        question = row['question']

        if (idx + 1) % 20 == 0:
            print(f"处理查询: {idx+1}/{len(topics_df)}")

        try:
            # 使用DPR检索
            passages, scores, passage_ids = retriever.search(question, k=4)

            # 生成TREC格式结果
            for rank, (passage_id, score) in enumerate(zip(passage_ids, scores), 1):
                results.append(f"{query_id} Q0 {passage_id} {rank} {score:.6f} romeo-juliet.dpr")

        except Exception as e:
            print(f"处理查询 {query_id} 时出错: {e}")
            continue

    # 保存结果
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))

    print(f"DPR检索结果保存到: {output_path}")
    print(f"生成了 {len(results)} 条结果")


if __name__ == "__main__":
    if not os.path.exists("data/topics.csv"):
        print("❌ 请在quantitative_eval目录中运行此脚本")
        exit(1)

    generate_dpr_run()
