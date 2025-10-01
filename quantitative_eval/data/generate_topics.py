import pandas as pd
import os
import csv
import re

def normalize_text(text):
    """标准化文本以便比较，去除标点符号差异"""
    # 移除所有撇号
    text = text.replace("'", "")
    # 标准化引号 - 将所有引号类型转换为简单的双引号
    text = text.replace('""', '"').replace('"', '"').replace('"', '"')
    # 移除多余空格
    text = ' '.join(text.split())
    return text.lower()

def replace_question_in_topics(q_txt_path, topics_csv_path, output_csv_path):
    """
    将Q.txt中对应topic的问题替换到topics.csv的question列
    txt中序号行对应csv的topic，序号行下的"- "开头行对应该topic的question列表
    """
    # -------------------------- 1. 解析Q.txt为topic-问题列表字典 --------------------------
    try:
        topic_questions = {}  # 存储{normalize_topic: [question1, question2, ...]}
        original_topics = {}  # 存储{normalize_topic: original_topic}
        current_topic = None
        current_questions = []

        with open(q_txt_path, 'r', encoding='UTF-8') as f:
            for line in f:
                line_stripped = line.strip()
                if not line_stripped:  # 跳过空行
                    continue

                # 匹配序号行（如"1. ..."）
                seq_match = re.match(r'^\d+\. (.*)$', line_stripped)
                if seq_match:
                    # 若已有当前topic，先存入字典
                    if current_topic is not None:
                        normalized_topic = normalize_text(current_topic)
                        topic_questions[normalized_topic] = current_questions
                        original_topics[normalized_topic] = current_topic
                    # 更新当前topic和问题列表
                    current_topic = seq_match.group(1).strip()  # 提取序号后的内容作为topic
                    current_questions = []
                # 匹配"- "开头的问题行
                elif line_stripped.startswith('- '):
                    if current_topic is None:
                        raise ValueError("Q.txt格式错误：问题行(- )出现在第一个序号行之前")
                    question = line_stripped[2:].strip()  # 去除"- "
                    current_questions.append(question)

        # 保存最后一个topic的问题列表
        if current_topic is not None:
            normalized_topic = normalize_text(current_topic)
            topic_questions[normalized_topic] = current_questions
            original_topics[normalized_topic] = current_topic

        # 验证txt解析结果
        if not topic_questions:
            raise ValueError("Q.txt中未解析到任何topic和问题")
        print(f"✅ 成功解析Q.txt：共{len(topic_questions)}个topic，问题数量分布：{[len(q) for q in topic_questions.values()]}")

    except FileNotFoundError:
        print(f"❌ 未找到Q.txt文件，请检查路径：{q_txt_path}")
        return
    except Exception as e:
        print(f"❌ 解析Q.txt时出错：{str(e)}")
        return

    # -------------------------- 2. 读取并验证topics.csv --------------------------
    try:
        df = pd.read_csv(
            topics_csv_path,
            encoding='UTF-8',
            sep=',',
            quotechar='"',
            na_filter=False
        )

        # 验证必需列
        required_cols = ['topic_id', 'topic', 'question_id', 'question']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"topics.csv缺少必需列，需包含：{required_cols}")

        # 按topic分组，检查每个topic的行数
        topic_groups = df.groupby('topic').groups

        # 创建标准化的topic映射
        csv_topic_mapping = {}  # {normalized_csv_topic: original_csv_topic}
        matched_topics = {}  # {original_csv_topic: normalized_txt_topic}

        for csv_topic in topic_groups:
            normalized_csv_topic = normalize_text(csv_topic)
            csv_topic_mapping[normalized_csv_topic] = csv_topic

            # 查找匹配的txt topic
            if normalized_csv_topic in topic_questions:
                matched_topics[csv_topic] = normalized_csv_topic
            else:
                # 尝试模糊匹配
                found_match = False
                for txt_normalized in topic_questions:
                    # 简单的模糊匹配，检查主要单词是否相同
                    csv_words = set(normalized_csv_topic.split())
                    txt_words = set(txt_normalized.split())
                    # 如果80%的单词匹配，认为是同一个topic
                    if len(csv_words & txt_words) / max(len(csv_words), len(txt_words)) > 0.8:
                        matched_topics[csv_topic] = txt_normalized
                        print(f"🔗 模糊匹配成功：CSV '{csv_topic[:50]}...' ↔ TXT '{original_topics[txt_normalized][:50]}...'")
                        found_match = True
                        break

                if not found_match:
                    print(f"⚠️  CSV中的topic未找到匹配：{csv_topic}")
                    # 继续处理，但跳过这个topic

        # 检查每个匹配topic的问题数量
        for csv_topic, txt_normalized in matched_topics.items():
            csv_row_count = len(topic_groups[csv_topic])
            txt_question_count = len(topic_questions[txt_normalized])
            if csv_row_count != txt_question_count:
                print(f"⚠️  topic '{csv_topic[:30]}...' 的问题数量不匹配：csv中有{csv_row_count}行，txt中有{txt_question_count}个问题")
                # 调整以较小的数量为准
                min_count = min(csv_row_count, txt_question_count)
                print(f"    将使用前{min_count}个问题进行替换")

        print(f"✅ 成功读取topics.csv：共{len(df)}条记录，{len(topic_groups)}个topic，其中{len(matched_topics)}个与Q.txt匹配")

    except FileNotFoundError:
        print(f"❌ 未找到topics.csv文件，请检查路径：{topics_csv_path}")
        return
    except Exception as e:
        print(f"❌ 读取topics.csv时出错：{str(e)}")
        return

    # -------------------------- 3. 按topic替换question列和topic列并保存 --------------------------
    try:
        replaced_count = 0
        # 遍历每个匹配的topic，替换对应的question和topic
        for csv_topic, txt_normalized in matched_topics.items():
            indices = topic_groups[csv_topic]
            questions = topic_questions[txt_normalized]
            original_topic = original_topics[txt_normalized]  # 获取Q.txt中的原始topic（带撇号）

            # 按索引顺序替换，使用较小的数量
            max_replacements = min(len(indices), len(questions))
            for i in range(max_replacements):
                df.at[indices[i], 'question'] = questions[i]
                df.at[indices[i], 'topic'] = original_topic  # 同时修复topic列
                replaced_count += 1

        # 保存文件
        df.to_csv(
            output_csv_path,
            encoding='UTF-8',
            index=False,
            sep=',',
            quotechar='"',
            quoting=csv.QUOTE_ALL
        )

        print(f"🎉 替换完成！共替换了{replaced_count}个问题，同时修复了topic列的撇号问题")
        print(f"💾 新文件已保存至：{output_csv_path}")
        print("\n📌 替换后前5条记录预览：")
        print(df.head()[['topic_id', 'topic', 'question_id', 'question']].to_string(index=False))

    except Exception as e:
        print(f"❌ 替换或保存文件时出错：{str(e)}")
        return

# -------------------------- 4. 配置路径并运行 --------------------------
if __name__ == "__main__":
    Q_TXT_PATH = "Q.txt"  # Q.txt文件路径
    TOPICS_CSV_PATH = "topics.csv"  # 原始topics.csv路径
    OUTPUT_CSV_PATH = "topics_updated.csv"  # 替换后输出的CSV路径

    replace_question_in_topics(Q_TXT_PATH, TOPICS_CSV_PATH, OUTPUT_CSV_PATH)