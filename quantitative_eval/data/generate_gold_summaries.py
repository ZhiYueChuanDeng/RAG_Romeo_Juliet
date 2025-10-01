#!/usr/bin/env python3
"""
基于现有CSV文件生成gold_summaries.csv

数据来源：
1. topics.csv: 提供question_id和对应的topic_id
2. core.csv: 提供summary内容 (core_A)
3. groundtruth.csv: 提供相关的passage_id

输出格式：
question_id | summary_id | summary | passage_id
"""

import pandas as pd
import csv


def generate_gold_summaries(topics_csv, core_csv, groundtruth_csv, output_csv):
    """
    基于现有CSV文件生成gold_summaries.csv
    """
    print("=== 开始生成gold_summaries.csv ===")

    # 1. 读取所有输入文件
    print("📖 读取输入文件...")

    try:
        # 读取topics.csv
        df_topics = pd.read_csv(topics_csv, encoding='utf-8')
        print(f"✅ 读取topics.csv: {len(df_topics)}条记录")

        # 读取core.csv - 尝试不同编码
        try:
            df_core = pd.read_csv(core_csv, encoding='utf-8')
        except UnicodeDecodeError:
            print("  尝试使用gbk编码读取core.csv...")
            df_core = pd.read_csv(core_csv, encoding='gbk')
        print(f"✅ 读取core.csv: {len(df_core)}条记录")

        # 读取groundtruth.csv - 尝试不同编码
        try:
            df_groundtruth = pd.read_csv(groundtruth_csv, encoding='utf-8')
        except UnicodeDecodeError:
            print("  尝试使用gbk编码读取groundtruth.csv...")
            df_groundtruth = pd.read_csv(groundtruth_csv, encoding='gbk')
        print(f"✅ 读取groundtruth.csv: {len(df_groundtruth)}条记录")

    except Exception as e:
        print(f"❌ 读取文件失败: {str(e)}")
        return

    # 2. 建立映射关系
    print("🔗 建立数据映射关系...")

    # 创建topic_id到core_A的映射 (W01 -> core_A)
    topic_to_summary = {}
    topic_to_summary_id = {}

    for _, row in df_core.iterrows():
        # 从Q101转换为W01格式
        core_q_id = row['core_Q_id']  # Q101
        topic_number = int(core_q_id[1:])  # 101
        topic_id = f"W{topic_number - 100:02d}"  # W01 (101-100=1)

        topic_to_summary[topic_id] = row['core_A']
        topic_to_summary_id[topic_id] = f"S{topic_number - 100:02d}"  # S01

    print(f"📋 建立了{len(topic_to_summary)}个topic到summary的映射")

    # 创建topic_id到passage_id的映射 (W01 -> [P001, P002, ...])
    topic_to_passages = {}

    for _, row in df_groundtruth.iterrows():
        # 从W001转换为W01格式
        groundtruth_topic_id = row['topic_id']  # W001
        if groundtruth_topic_id.startswith('W'):
            topic_number = groundtruth_topic_id[1:]  # 001
            topic_id = f"W{int(topic_number):02d}"  # W01

            if topic_id not in topic_to_passages:
                topic_to_passages[topic_id] = []
            topic_to_passages[topic_id].append(row['passage_id'])

    total_passages = sum(len(passages) for passages in topic_to_passages.values())
    print(f"📋 建立了{len(topic_to_passages)}个topic到passage的映射，共{total_passages}个passage")

    # 3. 生成gold_summaries数据
    print("🔄 生成gold_summaries数据...")

    gold_summaries_data = []

    for _, row in df_topics.iterrows():
        question_id = row['question_id']  # W01Q01
        topic_id = row['topic_id']  # W01

        # 获取对应的summary和summary_id
        if topic_id not in topic_to_summary:
            print(f"⚠️  警告：找不到topic_id {topic_id}对应的summary，跳过question {question_id}")
            continue

        summary = topic_to_summary[topic_id]
        summary_id = topic_to_summary_id[topic_id]

        # 获取对应的所有passage_id
        if topic_id not in topic_to_passages:
            print(f"⚠️  警告：找不到topic_id {topic_id}对应的passage，跳过question {question_id}")
            continue

        passage_ids = topic_to_passages[topic_id]

        # 为每个passage_id创建一条记录
        for passage_id in passage_ids:
            gold_summaries_data.append({
                'question_id': question_id,
                'summary_id': summary_id,
                'summary': summary,
                'passage_id': passage_id
            })

    # 4. 保存gold_summaries.csv
    print("💾 保存gold_summaries.csv...")

    try:
        df_gold_summaries = pd.DataFrame(gold_summaries_data)
        df_gold_summaries.to_csv(
            output_csv,
            encoding='utf-8',
            index=False,
            quoting=csv.QUOTE_ALL
        )

        print(f"✅ 成功保存gold_summaries.csv: {len(gold_summaries_data)}条记录")

        # 统计信息
        unique_questions = len(df_gold_summaries['question_id'].unique())
        unique_summaries = len(df_gold_summaries['summary_id'].unique())
        unique_passages = len(df_gold_summaries['passage_id'].unique())

        print(f"\n📊 统计信息:")
        print(f"  - 唯一question数量: {unique_questions}")
        print(f"  - 唯一summary数量: {unique_summaries}")
        print(f"  - 唯一passage数量: {unique_passages}")
        print(f"  - 总记录数量: {len(gold_summaries_data)}")

        # 预览前5条记录
        print(f"\n📌 前5条记录预览:")
        preview_cols = ['question_id', 'summary_id', 'passage_id']
        print(df_gold_summaries.head()[preview_cols].to_string(index=False))

    except Exception as e:
        print(f"❌ 保存文件失败: {str(e)}")
        return

    print("\n🎉 gold_summaries.csv生成完成！")


def main():
    """主函数"""
    TOPICS_CSV = "topics.csv"
    CORE_CSV = "core.csv"
    GROUNDTRUTH_CSV = "groundtruth.csv"
    OUTPUT_CSV = "gold_summaries.csv"

    print("基于现有CSV文件生成gold_summaries.csv")
    print("=" * 50)

    generate_gold_summaries(TOPICS_CSV, CORE_CSV, GROUNDTRUTH_CSV, OUTPUT_CSV)


if __name__ == "__main__":
    main()