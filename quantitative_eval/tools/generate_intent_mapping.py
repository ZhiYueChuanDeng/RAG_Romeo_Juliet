#!/usr/bin/env python3
"""
生成Romeo & Juliet项目的intent_mapping.csv
基于现有的topics.csv, groundtruth.csv和gold_summaries.csv生成意图映射
"""

import pandas as pd
import json
import re

def create_intent_name(topic):
    """
    基于topic内容生成意图名称
    例如: "What metaphor does Romeo use..." -> "Romeo_Metaphor_Juliet"
    """
    # 提取关键词来生成意图名
    topic_lower = topic.lower()

    # 定义意图映射规则
    intent_mapping = {
        'metaphor.*romeo.*juliet': 'Romeo_Metaphor_Juliet',
        'request.*juliet.*romeo.*identity': 'Juliet_Name_Request',
        'friar.*laurence.*agree.*marry': 'Friar_Marriage_Reason',
        'insult.*tybalt.*romeo': 'Tybalt_Insult_Romeo',
        'curse.*mercutio.*dying': 'Mercutio_Death_Curse',
        'romeo.*view.*banishment': 'Romeo_Banishment_View',
        'juliet.*potion.*friar': 'Juliet_Potion_Decision',
        'nurse.*advice.*juliet': 'Nurse_Advice_Juliet',
        'paris.*request.*marry': 'Paris_Marriage_Request',
        'capulet.*feast.*purpose': 'Capulet_Feast_Purpose',
        'romeo.*rosaline.*love': 'Romeo_Rosaline_Love',
        'balcony.*scene.*promise': 'Balcony_Scene_Promise',
        'wedding.*secret.*plan': 'Secret_Wedding_Plan',
        'sword.*fight.*outcome': 'Sword_Fight_Outcome',
        'poison.*tomb.*scene': 'Poison_Tomb_Scene',
        'families.*feud.*origin': 'Families_Feud_Origin',
        'love.*first.*sight': 'Love_First_Sight',
        'death.*tragic.*ending': 'Death_Tragic_Ending',
        'fate.*destiny.*theme': 'Fate_Destiny_Theme',
        'youth.*age.*conflict': 'Youth_Age_Conflict'
    }

    # 尝试匹配意图模式
    for pattern, intent_name in intent_mapping.items():
        if re.search(pattern, topic_lower):
            return intent_name

    # 如果没有匹配到，生成通用意图名
    # 提取主要角色和动作
    words = re.findall(r'\b[A-Z][a-z]+\b', topic)
    if len(words) >= 2:
        return f"{words[0]}_{words[1]}_Question"
    elif len(words) == 1:
        return f"{words[0]}_Question"
    else:
        return "General_Question"

def load_gold_summaries():
    """加载金标准答案"""
    try:
        gold_summaries = pd.read_csv('data/gold_summaries.csv')
        # 创建question_id到answer的映射 (从question_id提取topic_id)
        summary_dict = {}
        for _, row in gold_summaries.iterrows():
            question_id = row['question_id']
            topic_id = question_id[:3]  # W01Q01 -> W01
            answer = row['summary']
            if topic_id not in summary_dict:
                summary_dict[topic_id] = []
            if answer not in summary_dict[topic_id]:  # 避免重复
                summary_dict[topic_id].append(answer)
        return summary_dict
    except FileNotFoundError:
        print("Warning: gold_summaries.csv not found, will use placeholder answers")
        return {}

def generate_passage_hardcoded(topic_id, gold_summaries):
    """
    生成passage_hardcoded字段
    这个字段包含该意图的预设回答变体
    """
    if topic_id in gold_summaries:
        # 使用金标准答案
        answers = gold_summaries[topic_id]
        # 基于答案生成多个变体
        variations = []
        for answer in answers[:1]:  # 取第一个答案
            variations.extend([
                f"Based on Romeo and Juliet: {answer}",
                f"In Shakespeare's play: {answer}",
                f"According to the text: {answer}",
                f"From Romeo and Juliet: {answer}",
                f"In the play: {answer}"
            ])
        return json.dumps(variations[:5])  # 返回前5个变体
    else:
        # 生成通用回答
        generic_answers = [
            "Based on Romeo and Juliet, I can provide information about this topic.",
            "In Shakespeare's play, this is an important element of the story.",
            "According to the text, this plays a significant role in the narrative.",
            "From Romeo and Juliet, this contributes to the tragic tale.",
            "In the play, this aspect helps develop the characters and plot."
        ]
        return json.dumps(generic_answers)

def main():
    print("=== 生成Romeo & Juliet Intent Mapping ===")

    # 加载数据
    print("加载topics.csv...")
    topics_df = pd.read_csv('data/topics.csv')

    print("加载金标准答案...")
    gold_summaries = load_gold_summaries()

    # 创建intent mapping
    print("生成意图映射...")
    intent_mapping_data = []

    # 获取唯一的topics
    unique_topics = topics_df.drop_duplicates(['topic_id', 'topic'])

    for _, topic_row in unique_topics.iterrows():
        topic_id = topic_row['topic_id']
        topic = topic_row['topic']

        # 获取该topic的所有question变体
        topic_questions = topics_df[topics_df['topic_id'] == topic_id]

        # 生成意图名称
        intent_name = create_intent_name(topic)

        # 生成预设答案
        passage_hardcoded = generate_passage_hardcoded(topic_id, gold_summaries)

        # 为每个question变体创建记录
        for _, question_row in topic_questions.iterrows():
            record = {
                'topic_id': question_row['topic_id'],
                'topic': question_row['topic'],
                'question_id': question_row['question_id'],
                'question': question_row['question'],
                'intent': intent_name,
                'passage_hardcoded': passage_hardcoded
            }
            intent_mapping_data.append(record)

    # 创建DataFrame
    intent_mapping_df = pd.DataFrame(intent_mapping_data)

    # 保存文件
    output_file = 'data/intent_mapping.csv'
    intent_mapping_df.to_csv(output_file, index=False)

    print(f"\n生成完成！")
    print(f"输出文件: {output_file}")
    print(f"总记录数: {len(intent_mapping_df)}")
    print(f"唯一topic数: {intent_mapping_df['topic_id'].nunique()}")
    print(f"唯一intent数: {intent_mapping_df['intent'].nunique()}")

    # 显示意图统计
    print(f"\n意图分布:")
    intent_counts = intent_mapping_df['intent'].value_counts()
    for intent, count in intent_counts.head(10).items():
        print(f"  {intent}: {count}个问题")

    # 显示示例记录
    print(f"\n示例记录:")
    sample_record = intent_mapping_df.iloc[0]
    for col, val in sample_record.items():
        if col == 'passage_hardcoded':
            val = str(val)[:100] + "..." if len(str(val)) > 100 else val
        print(f"  {col}: {val}")

if __name__ == "__main__":
    main()