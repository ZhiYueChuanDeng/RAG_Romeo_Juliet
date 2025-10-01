#!/usr/bin/env python3
"""
分析Romeo & Juliet数据集中的问题类型
区分Known/Inferred/Out-of-KB问题
"""

import pandas as pd
from collections import defaultdict

def analyze_question_types():
    """分析数据集中的问题类型分布"""

    # 读取数据
    topics_df = pd.read_csv("data/topics.csv")
    gold_df = pd.read_csv("data/gold_summaries.csv")
    qrels_df = pd.read_csv("data/qrels.txt", sep="\t", header=None,
                           names=["question_id", "Q0", "passage_id", "relevance"])

    print("=" * 70)
    print("Romeo & Juliet 数据集问题类型分析")
    print("=" * 70)

    # 1. 统计基本信息
    all_questions = set(topics_df['question_id'])
    gold_questions = set(gold_df['question_id'])
    qrels_questions = set(qrels_df['question_id'])

    print(f"\n【数据集概览】")
    print(f"总问题数: {len(all_questions)}")
    print(f"有gold summary的问题: {len(gold_questions)}")
    print(f"有qrels的问题: {len(qrels_questions)}")

    # 2. 分析qrels中的相关性标签
    relevance_counts = qrels_df['relevance'].value_counts().sort_index()
    print(f"\n【Qrels相关性标签分布】")
    for rel, count in relevance_counts.items():
        print(f"标签 {rel}: {count} 条记录")

    # 3. 分类问题
    # Known: qrels中所有段落都是高度相关(label=2)
    # Inferred: qrels中有部分相关(label=1)的段落
    # Out-of-KB: 在topics中但不在qrels中

    known_questions = set()
    inferred_questions = set()

    for question_id in qrels_questions:
        question_qrels = qrels_df[qrels_df['question_id'] == question_id]
        relevance_labels = set(question_qrels['relevance'])

        if 1 in relevance_labels:
            # 有部分相关的段落 -> Inferred
            inferred_questions.add(question_id)
        elif relevance_labels == {2}:
            # 只有高度相关的段落 -> Known
            known_questions.add(question_id)

    out_of_kb_questions = all_questions - qrels_questions

    print(f"\n【问题分类结果】")
    print(f"Known (已知答案): {len(known_questions)} 个问题")
    print(f"Inferred (推断答案): {len(inferred_questions)} 个问题")
    print(f"Out-of-KB (知识库外): {len(out_of_kb_questions)} 个问题")
    print(f"总计: {len(known_questions) + len(inferred_questions) + len(out_of_kb_questions)}")

    # 4. 按topic统计
    print(f"\n【按Topic统计】")
    topics_df['question_type'] = topics_df['question_id'].apply(
        lambda q: 'Known' if q in known_questions
        else ('Inferred' if q in inferred_questions
              else 'Out-of-KB')
    )

    topic_stats = topics_df.groupby('topic_id')['question_type'].value_counts().unstack(fill_value=0)
    print(f"总topic数: {len(topic_stats)}")
    print(f"\n每个topic的问题类型分布统计:")
    print(topic_stats.describe())

    # 5. 检查每个问题的段落数量
    print(f"\n【段落数量分布】")
    passages_per_question = qrels_df.groupby('question_id').size()
    print(f"平均每个问题的相关段落数: {passages_per_question.mean():.2f}")
    print(f"最小段落数: {passages_per_question.min()}")
    print(f"最大段落数: {passages_per_question.max()}")

    # 显示段落数分布
    passage_dist = passages_per_question.value_counts().sort_index()
    print(f"\n段落数分布:")
    for num_passages, count in passage_dist.items():
        print(f"  {num_passages}个段落: {count}个问题")

    # 6. 示例问题
    print(f"\n【示例问题】")

    if len(known_questions) > 0:
        sample_known = list(known_questions)[0]
        print(f"\nKnown问题示例: {sample_known}")
        print(f"  问题: {topics_df[topics_df['question_id']==sample_known]['question'].iloc[0][:80]}...")
        known_qrels = qrels_df[qrels_df['question_id'] == sample_known]
        print(f"  相关段落: {list(known_qrels['passage_id'])}")
        print(f"  相关性标签: {list(known_qrels['relevance'])}")

    if len(inferred_questions) > 0:
        sample_inferred = list(inferred_questions)[0]
        print(f"\nInferred问题示例: {sample_inferred}")
        print(f"  问题: {topics_df[topics_df['question_id']==sample_inferred]['question'].iloc[0][:80]}...")
        inferred_qrels = qrels_df[qrels_df['question_id'] == sample_inferred]
        print(f"  相关段落: {list(inferred_qrels['passage_id'])}")
        print(f"  相关性标签: {list(inferred_qrels['relevance'])}")

    if len(out_of_kb_questions) > 0:
        sample_out = list(out_of_kb_questions)[0]
        print(f"\nOut-of-KB问题示例: {sample_out}")
        print(f"  问题: {topics_df[topics_df['question_id']==sample_out]['question'].iloc[0][:80]}...")
        print(f"  无相关段落（知识库中无答案）")

    # 7. 保存分类结果
    question_types = pd.DataFrame({
        'question_id': list(all_questions),
        'question_type': [
            'Known' if q in known_questions
            else ('Inferred' if q in inferred_questions
                  else 'Out-of-KB')
            for q in all_questions
        ]
    })

    output_file = "data/question_types.csv"
    question_types.to_csv(output_file, index=False)
    print(f"\n✅ 问题类型分类已保存到: {output_file}")

    return known_questions, inferred_questions, out_of_kb_questions

if __name__ == "__main__":
    import os

    # 确保在正确的目录
    if not os.path.exists("data/topics.csv"):
        print("❌ 请在quantitative_eval目录中运行此脚本")
        exit(1)

    analyze_question_types()
