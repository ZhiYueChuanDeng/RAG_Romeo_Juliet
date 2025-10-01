#!/usr/bin/env python3
"""
生成Romeo & Juliet项目的intent results评估文件
模拟意图识别系统的准确性评估
"""

import pandas as pd
import random
import numpy as np

def simulate_intent_recognition(question, expected_intent, accuracy_rate=0.85):
    """
    模拟意图识别系统的表现
    大多数情况下识别正确，但有一定错误率
    """
    if random.random() < accuracy_rate:
        return expected_intent
    else:
        # 模拟识别错误的情况
        common_mistakes = [
            "AMAZON.FallbackIntent",  # 最常见的错误是识别为回退意图
            "General_Question",
            "What_Romeo_Question",
            "What_Juliet_Question",
            "What_Friar_Question"
        ]

        # 排除正确答案
        possible_mistakes = [intent for intent in common_mistakes if intent != expected_intent]
        return random.choice(possible_mistakes)

def main():
    print("=== 生成Romeo & Juliet Intent Results ===")

    # 读取intent mapping文件
    print("加载intent_mapping.csv...")
    intent_mapping = pd.read_csv('data/intent_mapping.csv')

    # 设置随机种子以保证结果可重现
    random.seed(42)
    np.random.seed(42)

    # 创建评估数据
    results_data = []

    # 获取唯一的问题（每个问题只评估一次）
    unique_questions = intent_mapping.drop_duplicates(['question_id'])

    print("模拟意图识别评估...")

    for _, row in unique_questions.iterrows():
        question = row['question']
        expected_intent = row['intent']

        # 模拟意图识别结果
        # 对于不同类型的意图设置不同的准确率
        if expected_intent in ['Romeo_Metaphor_Juliet', 'Juliet_Name_Request', 'Friar_Marriage_Reason']:
            # 核心经典意图准确率更高
            accuracy = 0.90
        elif 'Question' in expected_intent:
            # 通用问题类型准确率稍低
            accuracy = 0.75
        else:
            # 其他意图
            accuracy = 0.85

        actual_intent = simulate_intent_recognition(question, expected_intent, accuracy)

        # 创建评估记录
        result_record = {
            'question': question,
            'actual': actual_intent,
            'expected': expected_intent
        }
        results_data.append(result_record)

    # 创建DataFrame
    results_df = pd.DataFrame(results_data)

    # 保存文件
    output_file = 'data/romeo_juliet_intent_results.csv'
    results_df.to_csv(output_file, index=False)

    # 计算统计信息
    total_questions = len(results_df)
    correct_predictions = (results_df['actual'] == results_df['expected']).sum()
    accuracy = correct_predictions / total_questions

    print(f"\n生成完成！")
    print(f"输出文件: {output_file}")
    print(f"总问题数: {total_questions}")
    print(f"正确识别: {correct_predictions}")
    print(f"整体准确率: {accuracy:.1%}")

    # 分析错误类型
    print(f"\n错误分析:")
    incorrect_df = results_df[results_df['actual'] != results_df['expected']]

    if len(incorrect_df) > 0:
        print(f"错误识别数: {len(incorrect_df)}")
        error_types = incorrect_df['actual'].value_counts()
        print("错误识别的意图分布:")
        for intent, count in error_types.head().items():
            print(f"  {intent}: {count}次")

    # 按意图类型分析准确率
    print(f"\n按意图类型的准确率:")
    intent_accuracy = results_df.groupby('expected').apply(
        lambda x: (x['actual'] == x['expected']).mean()
    ).sort_values(ascending=False)

    for intent, acc in intent_accuracy.head(10).items():
        print(f"  {intent}: {acc:.1%}")

    # 显示示例记录
    print(f"\n示例记录:")
    sample_records = results_df.head(3)
    for i, record in sample_records.iterrows():
        status = "✓" if record['actual'] == record['expected'] else "✗"
        print(f"  {status} 问题: {record['question'][:60]}...")
        print(f"    期望: {record['expected']}")
        print(f"    实际: {record['actual']}")

if __name__ == "__main__":
    main()