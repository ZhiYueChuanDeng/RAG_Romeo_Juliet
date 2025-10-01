#!/usr/bin/env python3
"""
Romeo and Juliet Text Processing Script
将原始文本分割成适合RAG系统的段落，并生成相应的数据文件
"""

import re
import csv
import json
from pathlib import Path

def clean_text(text):
    """清理文本，移除多余的空行和格式"""
    # 移除Project Gutenberg的头部信息
    lines = text.split('\n')
    start_idx = 0
    for i, line in enumerate(lines):
        if 'ACT I.' in line:
            start_idx = i
            break

    # 取从ACT I开始的内容
    content = '\n'.join(lines[start_idx:])

    # 清理Project Gutenberg的法律声明和技术信息
    content = re.sub(r'Information prepared by the Project Gutenberg legal advisor \d+', '', content)
    content = re.sub(r'Information prepared by the Project.*', '', content)

    # 清理其他Gutenberg相关内容
    content = re.sub(r'Project Gutenberg.*', '', content)
    content = re.sub(r'get or mget.*', '', content)
    content = re.sub(r'GET GUTINDEX.*', '', content)
    content = re.sub(r'cd etext\d+.*', '', content)
    content = re.sub(r'dir \[to see files\]', '', content)
    content = re.sub(r'\[to get files.*\]', '', content)

    # 清理页码和其他技术标记
    content = re.sub(r'Romeo and Juliet \d+', '', content)
    content = re.sub(r'\*\*\*.*?\*\*\*', '', content)  # 移除星号标记的内容

    # 清理多余空行
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

    return content.strip()

def split_by_scenes(text):
    """按场景分割文本"""
    scenes = []

    # 匹配ACT和Scene的模式
    act_pattern = r'(ACT [IVX]+\.)'
    scene_pattern = r'(Scene [IVX]+\. [^.]+\.)'

    # 找到所有ACT和Scene的位置
    act_matches = list(re.finditer(act_pattern, text))
    scene_matches = list(re.finditer(scene_pattern, text))

    all_markers = []

    # 收集所有标记点
    for match in act_matches:
        all_markers.append({
            'pos': match.start(),
            'type': 'act',
            'title': match.group(1).strip(),
            'full_match': match
        })

    for match in scene_matches:
        all_markers.append({
            'pos': match.start(),
            'type': 'scene',
            'title': match.group(1).strip(),
            'full_match': match
        })

    # 按位置排序
    all_markers.sort(key=lambda x: x['pos'])

    # 分割场景
    current_act = ""
    for i, marker in enumerate(all_markers):
        if marker['type'] == 'act':
            current_act = marker['title']
            continue

        if marker['type'] == 'scene':
            # 确定场景内容的起始和结束位置
            start_pos = marker['pos']

            # 找到下一个场景或ACT的位置作为结束点
            end_pos = len(text)
            for j in range(i + 1, len(all_markers)):
                if all_markers[j]['type'] in ['scene', 'act']:
                    end_pos = all_markers[j]['pos']
                    break

            # 提取场景内容
            scene_content = text[start_pos:end_pos].strip()

            # 进一步清理场景内容
            scene_content = re.sub(r'\[.*?\]', '', scene_content)  # 移除舞台指示
            scene_content = re.sub(r'Information prepared by.*', '', scene_content)  # 再次清理法律声明
            scene_content = re.sub(r'\n\s*\n+', '\n\n', scene_content)  # 清理空行

            if len(scene_content.strip()) > 100:  # 只保留有足够内容的场景
                scenes.append({
                    'act': current_act,
                    'scene': marker['title'],
                    'content': scene_content.strip()
                })

    return scenes

def generate_passages(scenes, max_passage_length=500):
    """将场景进一步分割成合适长度的段落"""
    passages = []
    passage_id = 1

    for scene in scenes:
        content = scene['content']

        # 按段落分割（空行分割）
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        current_passage = ""
        for paragraph in paragraphs:
            # 如果加上当前段落不会超长，就合并
            if len(current_passage + paragraph) <= max_passage_length:
                if current_passage:
                    current_passage += "\n\n" + paragraph
                else:
                    current_passage = paragraph
            else:
                # 保存当前段落
                if current_passage:
                    passages.append({
                        'passage_id': f'P{passage_id:03d}',
                        'act': scene['act'],
                        'scene': scene['scene'],
                        'passage': current_passage
                    })
                    passage_id += 1

                # 开始新段落
                current_passage = paragraph

        # 保存最后一个段落
        if current_passage:
            passages.append({
                'passage_id': f'P{passage_id:03d}',
                'act': scene['act'],
                'scene': scene['scene'],
                'passage': current_passage
            })
            passage_id += 1

    return passages

def generate_questions_from_passages(passages):
    """基于段落内容生成三种类型的问题"""
    questions = []

    # Type 1: 已知答案问题 - 直接从段落内容生成
    known_questions = []
    topic_id = 1

    for passage in passages:
        content = passage['passage'].lower()

        # 基于段落内容生成直接问题
        questions_for_passage = []

        # 人物出现检测
        if 'romeo' in content:
            questions_for_passage.extend([
                'What does Romeo do in this scene?',
                'How does Romeo behave here?',
                'What is Romeo\'s role in this part?'
            ])

        if 'juliet' in content:
            questions_for_passage.extend([
                'What does Juliet do in this scene?',
                'How does Juliet act here?',
                'What is Juliet\'s role in this part?'
            ])

        # 场景特定问题
        if 'balcony' in content or 'window' in content:
            questions_for_passage.extend([
                'What happens in the balcony scene?',
                'Describe the balcony scene',
                'What do the characters say on the balcony?'
            ])

        if 'fight' in content or 'sword' in content or 'death' in content:
            questions_for_passage.extend([
                'What conflict occurs in this scene?',
                'Describe the fight that takes place',
                'What violence happens here?'
            ])

        if 'love' in content or 'marry' in content or 'wedding' in content:
            questions_for_passage.extend([
                'How is love expressed in this scene?',
                'What romantic elements are present?',
                'How do the characters show affection?'
            ])

        # 为每个段落生成1-3个问题
        if questions_for_passage:
            selected_questions = questions_for_passage[:3]  # 取前3个
            known_questions.append({
                'topic_id': f'T{topic_id:03d}',
                'topic': f'Scene content from {passage["act"]} {passage["scene"]}',
                'questions': selected_questions,
                'passage_id': passage['passage_id'],
                'question_type': 'known'
            })
            topic_id += 1

    # Type 2: 推断答案问题 - 需要多个段落组合回答
    inferred_questions = [
        {
            'topic_id': f'T{topic_id:03d}',
            'topic': 'Character development throughout play',
            'questions': [
                'How does Romeo change throughout the play?',
                'What is Romeo\'s character arc?',
                'How does Romeo develop as a character?'
            ],
            'question_type': 'inferred'
        },
        {
            'topic_id': f'T{topic_id+1:03d}',
            'topic': 'Relationship progression',
            'questions': [
                'How does Romeo and Juliet\'s relationship develop?',
                'What stages do Romeo and Juliet go through?',
                'How does their love story unfold?'
            ],
            'question_type': 'inferred'
        },
        {
            'topic_id': f'T{topic_id+2:03d}',
            'topic': 'Family conflict impact',
            'questions': [
                'How does the family feud affect the story?',
                'What role does the family conflict play?',
                'How does the feud influence the characters?'
            ],
            'question_type': 'inferred'
        }
    ]
    topic_id += 3

    # Type 3: 知识库外问题 - 故意设计为段落中找不到答案的问题
    # 这些问题测试系统识别"无法回答"的能力，防止幻觉
    out_of_kb_questions = [
        {
            'topic_id': f'T{topic_id:03d}',
            'topic': 'Shakespeare\'s biography',
            'questions': [
                'When was William Shakespeare born?',
                'Where did Shakespeare live?',
                'What other plays did Shakespeare write besides Romeo and Juliet?',
                'How many children did Shakespeare have?'
            ],
            'question_type': 'out_of_kb'
        },
        {
            'topic_id': f'T{topic_id+1:03d}',
            'topic': 'Historical context',
            'questions': [
                'What was happening in England when Romeo and Juliet was written?',
                'Who was the monarch when Shakespeare wrote this play?',
                'What were the social customs in Elizabethan England?',
                'How did the plague affect theater in Shakespeare\'s time?'
            ],
            'question_type': 'out_of_kb'
        },
        {
            'topic_id': f'T{topic_id+2:03d}',
            'topic': 'Literary criticism',
            'questions': [
                'What do modern critics think of Romeo and Juliet?',
                'How is this play taught in schools today?',
                'What adaptations have been made of this play?',
                'Which actors are famous for playing Romeo?'
            ],
            'question_type': 'out_of_kb'
        },
        {
            'topic_id': f'T{topic_id+3:03d}',
            'topic': 'Production details',
            'questions': [
                'When was this play first performed?',
                'Which theater company first performed Romeo and Juliet?',
                'What costumes were used in the original production?',
                'How long does a typical performance last?'
            ],
            'question_type': 'out_of_kb'
        }
    ]

    # 合并所有问题
    all_questions = known_questions + inferred_questions + out_of_kb_questions

    return all_questions

def save_collection_csv(passages, filepath):
    """保存collection.csv文件"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['passage_id', 'passage'])
        for passage in passages:
            writer.writerow([passage['passage_id'], passage['passage']])
    print(f"Saved {len(passages)} passages to {filepath}")

def save_topics_csv(questions, filepath):
    """保存topics.csv文件"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['topic_id', 'Topic', 'question_id', 'question'])

        for topic in questions:
            for i, question in enumerate(topic['questions'], 1):
                question_id = f"{topic['topic_id']}Q{i:02d}"
                writer.writerow([topic['topic_id'], topic['topic'], question_id, question])

    total_questions = sum(len(topic['questions']) for topic in questions)
    print(f"Saved {total_questions} questions for {len(questions)} topics to {filepath}")

def main():
    # 读取原始文本
    input_file = 'RomeoandJuliet.txt'

    if not Path(input_file).exists():
        print(f"Error: {input_file} not found!")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    print("Processing Romeo and Juliet text...")

    # 清理文本
    clean_content = clean_text(raw_text)

    # 按场景分割
    scenes = split_by_scenes(clean_content)
    print(f"Found {len(scenes)} scenes")

    # 生成段落
    passages = generate_passages(scenes)
    print(f"Generated {len(passages)} passages")

    # 生成问题（基于段落内容）
    questions = generate_questions_from_passages(passages)

    # 保存文件
    save_collection_csv(passages, 'collection.csv')
    save_topics_csv(questions, 'topics.csv')

    # 创建简单的qrels.txt（需要手工标注相关性）
    with open('qrels.txt', 'w') as f:
        f.write("# This file needs manual annotation\n")
        f.write("# Format: question_id 0 passage_id relevance_score\n")
        f.write("# Example: T001Q01 0 P001 2\n")

    print("\nNext steps:")
    print("1. Review generated passages in collection.csv")
    print("2. Add more questions to topics.csv if needed")
    print("3. Manually create relevance judgments in qrels.txt")
    print("4. Generate groundtruth.csv based on qrels.txt")

if __name__ == "__main__":
    main()