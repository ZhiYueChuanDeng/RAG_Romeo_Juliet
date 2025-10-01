#!/usr/bin/env python3
"""
测试Romeo & Juliet Alexa集成
模拟Alexa Skill的基本功能测试
"""

import json
import random

def load_interaction_model():
    """加载交互模型"""
    try:
        with open('src/intent-based/interactionModels/custom/en-US-complete.json', 'r', encoding='utf-8') as f:
            model = json.load(f)
        return model
    except FileNotFoundError:
        print("Error: Interaction model file not found!")
        return None

def load_intent_mapping():
    """加载意图映射"""
    try:
        import pandas as pd
        intent_df = pd.read_csv('data/intent_mapping.csv')
        return intent_df
    except Exception as e:
        print(f"Error loading intent mapping: {e}")
        return None

def find_matching_intent(user_input, interaction_model):
    """
    简单的意图匹配模拟
    在实际Alexa中，这由NLU引擎处理
    """
    user_input_lower = user_input.lower()

    intents = interaction_model['interactionModel']['languageModel']['intents']

    # 按匹配分数排序
    matches = []

    for intent in intents:
        intent_name = intent['name']

        # 跳过Amazon内置意图的匹配
        if intent_name.startswith('AMAZON.'):
            continue

        samples = intent.get('samples', [])

        # 计算匹配分数
        max_score = 0
        for sample in samples:
            sample_words = set(sample.lower().split())
            user_words = set(user_input_lower.split())

            # 简单的词汇重叠分数
            overlap = len(sample_words.intersection(user_words))
            score = overlap / len(sample_words.union(user_words)) if sample_words.union(user_words) else 0

            max_score = max(max_score, score)

        if max_score > 0:
            matches.append((intent_name, max_score))

    # 返回最佳匹配
    if matches:
        matches.sort(key=lambda x: x[1], reverse=True)
        if matches[0][1] > 0.2:  # 最小匹配阈值
            return matches[0][0]

    return "AMAZON.FallbackIntent"

def get_intent_response(intent_name, intent_df):
    """获取意图的响应"""
    if intent_name == "AMAZON.FallbackIntent":
        return "I didn't understand that question about Romeo and Juliet. Try asking about specific characters, scenes, or themes."

    # 查找意图的响应
    intent_rows = intent_df[intent_df['intent'] == intent_name]
    if not intent_rows.empty:
        passage_hardcoded = intent_rows.iloc[0]['passage_hardcoded']
        try:
            responses = json.loads(passage_hardcoded)
            return random.choice(responses)
        except json.JSONDecodeError:
            return f"I can tell you about {intent_name.replace('_', ' ').lower()}."

    return f"I found information about {intent_name.replace('_', ' ').lower()}."

def simulate_alexa_response(user_input, interaction_model, intent_df):
    """模拟完整的Alexa响应流程"""
    print(f"\n👤 User: {user_input}")

    # 意图识别
    matched_intent = find_matching_intent(user_input, interaction_model)
    print(f"🧠 Matched Intent: {matched_intent}")

    # 生成响应
    response = get_intent_response(matched_intent, intent_df)
    print(f"🤖 Alexa: {response}")

    return matched_intent, response

def run_test_scenarios():
    """运行预定义的测试场景"""

    # 加载数据
    print("=== Romeo & Juliet Alexa Integration Test ===")

    interaction_model = load_interaction_model()
    intent_df = load_intent_mapping()

    if not interaction_model or intent_df is None:
        print("Failed to load required files!")
        return

    print(f"✅ Loaded interaction model with {len(interaction_model['interactionModel']['languageModel']['intents'])} intents")
    print(f"✅ Loaded intent mapping with {len(intent_df)} records")

    # 测试场景
    test_scenarios = [
        # 核心意图测试
        "What metaphor does Romeo use for Juliet?",
        "What does Juliet ask Romeo about his name?",
        "Why does Friar Laurence help them marry?",
        "What insult does Tybalt say to Romeo?",
        "What curse does Mercutio utter?",
        "How does Romeo feel about banishment?",

        # 变体测试
        "Romeo's metaphor for Juliet",
        "Juliet's request about Romeo's identity",
        "Friar's motivation for marriage",

        # 通用问题
        "Tell me about Romeo and Juliet",
        "What is the story about?",

        # 应该触发fallback的问题
        "What's the weather like?",
        "How do I cook pasta?",
        "Tell me a joke"
    ]

    print(f"\n🧪 Running {len(test_scenarios)} test scenarios...\n")

    results = []

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"--- Test {i}/{len(test_scenarios)} ---")
        intent, response = simulate_alexa_response(scenario, interaction_model, intent_df)
        results.append({
            'input': scenario,
            'intent': intent,
            'response': response[:100] + "..." if len(response) > 100 else response
        })

    # 统计结果
    print(f"\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)

    intent_counts = {}
    for result in results:
        intent = result['intent']
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

    print(f"Intent Distribution:")
    for intent, count in sorted(intent_counts.items()):
        print(f"  {intent}: {count} times")

    # 显示成功识别的核心意图
    core_intents = [
        'Romeo_Metaphor_Juliet', 'Juliet_Name_Request', 'Friar_Marriage_Reason',
        'Tybalt_Insult_Romeo', 'Mercutio_Death_Curse', 'Romeo_Banishment_View'
    ]

    core_matches = sum(1 for result in results if result['intent'] in core_intents)
    print(f"\n核心意图识别成功率: {core_matches}/{len(core_intents)} = {core_matches/len(core_intents):.1%}")

    fallback_count = intent_counts.get('AMAZON.FallbackIntent', 0)
    print(f"Fallback触发次数: {fallback_count}/{len(test_scenarios)} = {fallback_count/len(test_scenarios):.1%}")

def interactive_test():
    """交互式测试模式"""
    print(f"\n🎮 Interactive Test Mode")
    print("Type your questions about Romeo and Juliet (or 'quit' to exit):")

    interaction_model = load_interaction_model()
    intent_df = load_intent_mapping()

    if not interaction_model or intent_df is None:
        print("Failed to load required files!")
        return

    while True:
        user_input = input(f"\n👤 You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("🤖 Alexa: Goodbye! Thank you for exploring Romeo and Juliet with me!")
            break

        if not user_input:
            continue

        simulate_alexa_response(user_input, interaction_model, intent_df)

def main():
    print("Choose test mode:")
    print("1. Run predefined test scenarios")
    print("2. Interactive test mode")
    print("3. Both")

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice in ['1', '3']:
        run_test_scenarios()

    if choice in ['2', '3']:
        interactive_test()

if __name__ == "__main__":
    main()