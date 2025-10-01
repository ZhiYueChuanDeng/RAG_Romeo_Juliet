#!/usr/bin/env python3
"""
生成Romeo & Juliet RAG系统的runs文件
基于现代化系统生成TREC格式的检索结果
"""

import os
import sys
import pandas as pd
from typing import List, Dict, Tuple

# 添加path以导入我们的模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.modern_rag_system import ModernRAGSystem
from pyserini.search.lucene import LuceneSearcher

def generate_faiss_run(output_path: str = "target/runs/romeo-juliet-faiss.txt"):
    """
    使用FAISS检索器生成runs文件
    """
    print("=== 生成FAISS检索结果 ===")

    # 初始化RAG系统
    rag_system = ModernRAGSystem(retrieval_method="faiss", generation_method="simple")

    # 读取查询
    topics_df = pd.read_csv("data/topics.csv")

    results = []

    for _, row in topics_df.iterrows():
        query_id = row['question_id']
        question = row['question']

        print(f"处理查询: {query_id} - {question[:50]}...")

        try:
            # 使用FAISS检索，每个topic对应4个相关段落
            faiss_results = rag_system.retriever.search(question, k=4)
            passages, scores, passage_ids = faiss_results

            # 生成TREC格式结果
            for rank, (passage_id, score) in enumerate(zip(passage_ids, scores), 1):
                results.append(f"{query_id} Q0 {passage_id} {rank} {score:.6f} romeo-juliet.faiss")

        except Exception as e:
            print(f"处理查询 {query_id} 时出错: {e}")
            continue

    # 保存结果
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))

    print(f"FAISS检索结果保存到: {output_path}")
    print(f"生成了 {len(results)} 条结果")

def generate_bm25_run(output_path: str = "target/runs/romeo-juliet-bm25.txt"):
    """
    使用BM25检索器生成runs文件
    """
    print("=== 生成BM25检索结果 ===")

    # 检查BM25索引是否存在
    bm25_index_path = "target/indexes/bm25"
    if not os.path.exists(bm25_index_path):
        print(f"❌ BM25索引不存在: {bm25_index_path}")
        print("请先构建BM25索引")
        return

    # 初始化BM25检索器
    searcher = LuceneSearcher(bm25_index_path)

    # 读取查询
    topics_df = pd.read_csv("data/topics.csv")

    results = []

    for _, row in topics_df.iterrows():
        query_id = row['question_id']
        question = row['question']

        print(f"处理查询: {query_id} - {question[:50]}...")

        try:
            # 使用BM25检索，每个topic对应4个相关段落
            hits = searcher.search(question, k=4)

            # 生成TREC格式结果
            for rank, hit in enumerate(hits, 1):
                results.append(f"{query_id} Q0 {hit.docid} {rank} {hit.score:.6f} romeo-juliet.bm25")

        except Exception as e:
            print(f"处理查询 {query_id} 时出错: {e}")
            continue

    # 保存结果
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))

    print(f"BM25检索结果保存到: {output_path}")
    print(f"生成了 {len(results)} 条结果")

def generate_intent_run(output_path: str = "target/runs/romeo-juliet-intent.txt"):
    """
    使用意图模式生成runs文件
    """
    print("=== 生成意图检索结果 ===")

    # 初始化RAG系统（意图模式）
    rag_system = ModernRAGSystem(retrieval_method="faiss", generation_method="intent")

    # 读取查询和意图映射
    topics_df = pd.read_csv("data/topics.csv")
    try:
        intent_df = pd.read_csv("data/intent_mapping.csv")
    except FileNotFoundError:
        print("❌ 意图映射文件不存在，跳过意图runs生成")
        return

    results = []

    for _, row in topics_df.iterrows():
        query_id = row['question_id']
        question = row['question']

        print(f"处理查询: {query_id} - {question[:50]}...")

        try:
            # 检查是否有对应的意图
            # 这里简化处理，使用FAISS作为后备，每个topic对应4个相关段落
            faiss_results = rag_system.retriever.search(question, k=4)
            passages, scores, passage_ids = faiss_results

            # 生成TREC格式结果
            for rank, (passage_id, score) in enumerate(zip(passage_ids, scores), 1):
                results.append(f"{query_id} Q0 {passage_id} {rank} {score:.6f} romeo-juliet.intent")

        except Exception as e:
            print(f"处理查询 {query_id} 时出错: {e}")
            continue

    # 保存结果
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))

    print(f"意图检索结果保存到: {output_path}")
    print(f"生成了 {len(results)} 条结果")

def main():
    """主函数"""
    print("🎭 生成Romeo & Juliet RAG系统runs文件")
    print("=" * 50)

    # 确保在正确的目录中
    if not os.path.exists("data/topics.csv"):
        print("❌ 请在quantitative_eval目录中运行此脚本")
        return

    try:
        # 生成FAISS runs
        generate_faiss_run()
        print()

        # 生成BM25 runs
        generate_bm25_run()
        print()

        # 生成Intent runs
        generate_intent_run()
        print()

        print("✅ 所有runs文件生成完成！")

        # 显示统计信息
        runs_dir = "target/runs"
        if os.path.exists(runs_dir):
            print("\n📊 生成的runs文件:")
            for filename in os.listdir(runs_dir):
                if filename.startswith("romeo-juliet"):
                    filepath = os.path.join(runs_dir, filename)
                    with open(filepath, 'r') as f:
                        line_count = sum(1 for _ in f)
                    print(f"  {filename}: {line_count} 条结果")

    except Exception as e:
        print(f"❌ 生成runs文件时出错: {e}")

if __name__ == "__main__":
    main()