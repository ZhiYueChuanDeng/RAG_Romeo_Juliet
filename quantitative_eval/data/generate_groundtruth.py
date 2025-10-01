#!/usr/bin/env python3
"""
基于core.csv和P.txt生成groundtruth.csv文件

数据来源：
1. core.csv：提供topic_id, topic, relevance_judgment
2. P.txt：提供passage变体（序号行对应core_A，"- "开头行为变体）

输出格式：
topic_id | topic | passage_id | passage | relevance_judgment
"""

import csv
import re
import pandas as pd


def parse_passages_from_file(p_txt_path):
    """
    解析P.txt文件，提取序号行（原core_A）和对应的变体
    返回格式：{序号: [变体1, 变体2, 变体3, 变体4]}
    """
    passages = {}  # {序号: [passage_list]}
    current_number = None
    current_passages = []

    with open(p_txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_stripped = line.strip()
            if not line_stripped:  # 跳过空行
                continue

            # 匹配序号行（如"1. Romeo uses..."）
            number_match = re.match(r'^(\d+)\. (.*)$', line_stripped)
            if number_match:
                # 保存上一个序号的变体
                if current_number is not None:
                    passages[current_number] = current_passages

                # 开始新的序号
                current_number = int(number_match.group(1))
                original_text = number_match.group(2).strip()
                current_passages = [original_text]  # 原文本作为第一个变体

            # 匹配变体行（如"- Romeo employs..."）
            elif line_stripped.startswith('- '):
                if current_number is None:
                    raise ValueError("P.txt格式错误：变体行出现在第一个序号行之前")

                variant = line_stripped[2:].strip()  # 去除"- "
                current_passages.append(variant)

    # 保存最后一个序号的变体
    if current_number is not None:
        passages[current_number] = current_passages

    return passages


def generate_groundtruth_csv(core_csv_path, p_txt_path, output_csv_path):
    """
    基于core.csv和P.txt生成groundtruth.csv
    """
    print("=== 开始生成groundtruth.csv ===")

    # 1. 解析P.txt
    print("📖 解析P.txt文件...")
    try:
        passages = parse_passages_from_file(p_txt_path)
        total_passages = sum(len(variants) for variants in passages.values())
        print(f"✅ 成功解析P.txt：共{len(passages)}个序号，{total_passages}个passage变体")
    except Exception as e:
        print(f"❌ 解析P.txt失败：{str(e)}")
        return

    # 2. 读取core.csv
    print("📖 读取core.csv文件...")
    try:
        df_core = pd.read_csv(core_csv_path, encoding='utf-8')

        # 验证必需列
        required_cols = ['core_Q_id', 'core_Q', 'core_A', 'relevance_judgment']
        missing_cols = [col for col in required_cols if col not in df_core.columns]
        if missing_cols:
            raise ValueError(f"core.csv缺少必需列：{missing_cols}")

        print(f"✅ 成功读取core.csv：共{len(df_core)}条记录")
    except Exception as e:
        print(f"❌ 读取core.csv失败：{str(e)}")
        return

    # 3. 生成groundtruth数据
    print("🔄 生成groundtruth数据...")
    groundtruth_data = []
    passage_id_counter = 1

    for index, row in df_core.iterrows():
        # 提取core.csv数据
        topic_id = row['core_Q_id'].replace('Q', 'W')  # Q001 -> W01
        topic = row['core_Q']
        relevance_judgment = row['relevance_judgment']

        # 获取对应的passage变体
        row_number = index + 1  # P.txt中的序号从1开始
        if row_number not in passages:
            print(f"⚠️  警告：core.csv第{row_number}行在P.txt中未找到对应变体，跳过")
            continue

        passage_variants = passages[row_number]

        # 为每个变体创建一条记录
        for passage in passage_variants:
            passage_id = f"P{passage_id_counter:03d}"  # P001, P002, ...

            groundtruth_data.append({
                'topic_id': topic_id,
                'topic': topic,
                'passage_id': passage_id,
                'passage': passage,
                'relevance_judgment': relevance_judgment
            })

            passage_id_counter += 1

    # 4. 保存groundtruth.csv
    print("💾 保存groundtruth.csv文件...")
    try:
        df_groundtruth = pd.DataFrame(groundtruth_data)
        df_groundtruth.to_csv(
            output_csv_path,
            encoding='utf-8',
            index=False,
            quoting=csv.QUOTE_ALL
        )

        print(f"✅ 成功保存groundtruth.csv：共{len(groundtruth_data)}条记录")

        # 统计信息
        unique_topics = len(df_groundtruth['topic_id'].unique())
        avg_passages_per_topic = len(groundtruth_data) / unique_topics if unique_topics > 0 else 0

        print(f"\n📊 统计信息：")
        print(f"  - 唯一topic数量：{unique_topics}")
        print(f"  - 总passage数量：{len(groundtruth_data)}")
        print(f"  - 平均每topic的passage数量：{avg_passages_per_topic:.1f}")

        # 预览前5条记录
        print(f"\n📌 前5条记录预览：")
        print(df_groundtruth.head()[['topic_id', 'passage_id', 'relevance_judgment']].to_string(index=False))

    except Exception as e:
        print(f"❌ 保存文件失败：{str(e)}")
        return

    print("\n🎉 groundtruth.csv生成完成！")


def main():
    """主函数"""
    CORE_CSV_PATH = "core.csv"
    P_TXT_PATH = "P.txt"
    OUTPUT_CSV_PATH = "groundtruth.csv"

    print("基于core.csv和P.txt生成groundtruth.csv")
    print("=" * 50)

    generate_groundtruth_csv(CORE_CSV_PATH, P_TXT_PATH, OUTPUT_CSV_PATH)


if __name__ == "__main__":
    main()