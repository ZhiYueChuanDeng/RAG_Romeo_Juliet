#!/usr/bin/env python3
"""
基于intent_mapping.csv生成完整的Alexa Intent Handlers
自动为所有Romeo & Juliet意图创建Lambda函数处理器
"""

import pandas as pd
import json
from collections import defaultdict

def load_intent_mapping():
    """加载意图映射数据"""
    try:
        intent_df = pd.read_csv('data/intent_mapping.csv')
        return intent_df
    except FileNotFoundError:
        print("Error: intent_mapping.csv not found!")
        return None

def extract_intent_responses(intent_df):
    """提取每个意图的响应变体"""
    intent_responses = {}

    # 获取唯一的意图
    unique_intents = intent_df.drop_duplicates(['intent'])

    for _, row in unique_intents.iterrows():
        intent_name = row['intent']
        passage_hardcoded = row['passage_hardcoded']

        try:
            # 解析JSON格式的响应变体
            responses = json.loads(passage_hardcoded)
            intent_responses[intent_name] = responses
        except json.JSONDecodeError:
            # 如果JSON解析失败，使用默认响应
            intent_responses[intent_name] = [
                f"Based on Romeo and Juliet, I can provide information about this topic.",
                f"In Shakespeare's play, this is an important element of the story.",
                f"According to the text, this aspect is significant to the plot."
            ]

    return intent_responses

def extract_sample_utterances(intent_df):
    """提取每个意图的示例话语"""
    intent_samples = defaultdict(list)

    for _, row in intent_df.iterrows():
        intent_name = row['intent']
        question = row['question']

        # 清理问题文本作为示例话语
        cleaned_question = question.replace('"', '').replace("'", "").strip()
        if cleaned_question not in intent_samples[intent_name]:
            intent_samples[intent_name].append(cleaned_question)

    return dict(intent_samples)

def generate_handler_class(intent_name, responses):
    """生成单个意图处理器类的代码"""
    class_name = f"{intent_name}IntentHandler"

    # 转换响应为Python列表格式
    responses_str = '[\n'
    for response in responses:
        escaped_response = response.replace('"', '\\"')
        responses_str += f'        "{escaped_response}",\n'
    responses_str += '    ]'

    handler_code = f'''class {class_name}(AbstractRequestHandler):
    """Handler for {intent_name} intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("{intent_name}")(handler_input)

    def handle(self, handler_input):
        responses = {responses_str}

        speak_output = random.choice(responses)

        ask_variations = [
            'Would you like to know more about Romeo and Juliet?',
            "What else would you like to explore about the play?",
            "Is there another aspect of Romeo and Juliet you'd like to discuss?",
            "Any other questions about the story?"
        ]
        ask_output = random.choice(ask_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )
'''
    return handler_code, class_name

def generate_interaction_model(intent_samples):
    """生成完整的Alexa交互模型JSON"""
    intents = []

    # 添加Romeo & Juliet特定意图
    for intent_name, samples in intent_samples.items():
        intent_obj = {
            "name": intent_name,
            "slots": [],
            "samples": samples[:8]  # 限制每个意图最多8个示例
        }
        intents.append(intent_obj)

    # 添加标准Amazon意图
    standard_intents = [
        {
            "name": "AMAZON.StopIntent",
            "samples": [
                "that is all i needed thank you",
                "nothing else thank you",
                "bye",
                "goodbye",
                "stop",
                "quit",
                "exit",
                "that will be all"
            ]
        },
        {
            "name": "AMAZON.CancelIntent",
            "samples": [
                "cancel",
                "nevermind",
                "forget it",
                "cancel that"
            ]
        },
        {
            "name": "AMAZON.HelpIntent",
            "samples": [
                "help",
                "what can you do",
                "what are your capabilities",
                "how can you help me",
                "what questions can I ask",
                "what do you know",
                "help me",
                "I need help"
            ]
        },
        {
            "name": "AMAZON.FallbackIntent",
            "samples": []
        }
    ]

    intents.extend(standard_intents)

    interaction_model = {
        "interactionModel": {
            "languageModel": {
                "invocationName": "romeo bot",
                "intents": intents,
                "types": []
            }
        }
    }

    return interaction_model

def main():
    print("=== 生成完整的Alexa Handlers ===")

    # 加载数据
    intent_df = load_intent_mapping()
    if intent_df is None:
        return

    # 提取意图响应和示例话语
    intent_responses = extract_intent_responses(intent_df)
    intent_samples = extract_sample_utterances(intent_df)

    print(f"找到 {len(intent_responses)} 个意图")

    # 生成Lambda函数代码
    print("生成Lambda函数处理器...")

    handler_classes = []
    handler_registrations = []

    for intent_name, responses in intent_responses.items():
        handler_code, class_name = generate_handler_class(intent_name, responses)
        handler_classes.append(handler_code)
        handler_registrations.append(f"sb.add_request_handler({class_name}())")

    # 生成完整的Lambda函数文件
    lambda_template = '''# -*- coding: utf-8 -*-

# Romeo & Juliet RAG Question-Answering System - Complete Alexa Skills Kit Integration
# Auto-generated from intent_mapping.csv

import logging
import ask_sdk_core.utils as ask_utils
import json
import random

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        response_variations = [
            "Welcome to the Romeo and Juliet assistant! I can answer questions about Shakespeare's tragic love story.",
            "Greetings! I'm here to help with questions about Romeo and Juliet. What would you like to know?",
            "Hello! I can assist you with questions about the characters, plot, and themes in Romeo and Juliet.",
            "Welcome! Ask me anything about Romeo and Juliet - from character motivations to famous quotes."
        ]

        speak_output = random.choice(response_variations)

        ask_variations = [
            'What would you like to know about Romeo and Juliet?',
            "Feel free to ask about any character, scene, or theme from the play.",
            "What aspect of Romeo and Juliet interests you?",
            "Ask me about the star-crossed lovers or any other element of the story."
        ]

        ask_output = random.choice(ask_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        response_variations = [
            "I can answer questions about Romeo and Juliet, including character analysis, plot events, themes, and famous quotes. For example, you can ask me about Romeo's metaphors for Juliet, or what curse Mercutio utters.",
            "Ask me about any aspect of Shakespeare's Romeo and Juliet - characters like Romeo, Juliet, Mercutio, or Tybalt, plot events, themes like love and fate, or famous scenes.",
            "I'm here to help with Romeo and Juliet questions. You can ask about character motivations, plot developments, literary devices, or specific scenes from the play."
        ]

        speak_output = random.choice(response_variations)
        ask_output = "What would you like to know about Romeo and Juliet?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        response_variations = [
            "Thank you for exploring Romeo and Juliet with me. May your love of literature continue to grow!",
            "Farewell! I hope I've helped illuminate the beauty of Shakespeare's Romeo and Juliet.",
            "Goodbye! Remember, 'These violent delights have violent ends.' Until next time!",
            "Thank you for your questions about Romeo and Juliet. Keep exploring the world of literature!"
        ]

        speak_output = random.choice(response_variations)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent - integration point for FAISS."""
    def __init__(self):
        self.fallback_count = 0

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        self.fallback_count += 1

        if self.fallback_count >= 30:
            return handler_input.response_builder.speak(
                "I'm having technical difficulties right now. Please try again later. Thank you for your patience."
            ).set_should_end_session(True).response
        else:
            # TODO: In production, integrate FAISS retrieval here
            response_variations = [
                "I didn't understand that question about Romeo and Juliet. Try asking about specific characters, scenes, or themes.",
                "I'm not sure about that. You can ask me about Romeo's love for Juliet, the family feud, or specific scenes from the play.",
                "That question isn't clear to me. Try asking about character motivations, plot events, or famous quotes from Romeo and Juliet."
            ]

            speak_output = random.choice(response_variations)
            reprompt = "What would you like to know about Romeo and Juliet?"

            return handler_input.response_builder.speak(speak_output).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

# Romeo & Juliet Specific Intent Handlers (Auto-generated)

{handler_classes}

class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector for debugging."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = f"You just triggered the {{intent_name}} intent."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling."""
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble answering your question about Romeo and Juliet. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill
sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Auto-generated Romeo & Juliet specific handlers
{handler_registrations}

sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()'''

    # 组装完整代码
    all_handlers = '\n\n'.join(handler_classes)
    all_registrations = '\n'.join(handler_registrations)

    complete_lambda = lambda_template.format(
        handler_classes=all_handlers,
        handler_registrations=all_registrations
    )

    # 保存Lambda函数
    lambda_output = 'src/intent-based/lambda/lambda_function_complete.py'
    with open(lambda_output, 'w', encoding='utf-8') as f:
        f.write(complete_lambda)

    # 生成交互模型
    print("生成交互模型...")
    interaction_model = generate_interaction_model(intent_samples)

    # 保存交互模型
    model_output = 'src/intent-based/interactionModels/custom/en-US-complete.json'
    with open(model_output, 'w', encoding='utf-8') as f:
        json.dump(interaction_model, f, indent=2, ensure_ascii=False)

    print(f"\n生成完成！")
    print(f"Lambda函数文件: {lambda_output}")
    print(f"交互模型文件: {model_output}")
    print(f"生成了 {len(handler_classes)} 个意图处理器")
    print(f"交互模型包含 {len(interaction_model['interactionModel']['languageModel']['intents'])} 个意图")

    # 显示意图统计
    print(f"\n意图列表:")
    for i, intent_name in enumerate(intent_responses.keys(), 1):
        sample_count = len(intent_samples.get(intent_name, []))
        print(f"  {i:2d}. {intent_name} ({sample_count} samples)")

if __name__ == "__main__":
    main()