#!/usr/bin/env python3
"""
Romeo & Juliet RAG系统 - 统一入口点
提供所有功能的友好访问接口
"""

import os
import sys
from typing import Optional

def print_banner():
    """打印系统横幅"""
    banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║         🎭 Romeo & Juliet RAG Question-Answering System        ║
    ║                                                                ║
    ║    "What's in a name? That which we call a rose by any         ║
    ║     other name would smell as sweet." - Juliet                 ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def show_main_menu():
    """显示主菜单"""
    print("\n🎯 请选择要使用的功能:")
    print("=" * 60)
    print("1. 💬 文本问答 (现代FAISS语义检索)")
    print("2. 🎤 语音问答 (完整语音RAG系统)")
    print("3. 📊 性能评估 (FAISS vs BM25对比)")
    print("4. 🧪 简单测试 (TF-IDF检索)")
    print("5. 🔧 系统管理 (索引构建、数据生成等)")
    print("6. 📖 项目信息 (关于本系统)")
    print("0. 🚪 退出系统")
    print("=" * 60)

def text_qa_menu():
    """文本问答菜单"""
    print("\n💬 文本问答系统")
    print("选择配置:")
    print("1. FAISS + 简单生成 (推荐)")
    print("2. FAISS + Falcon生成 (1文档)")
    print("3. FAISS + Falcon生成 (3文档)")
    print("4. FAISS + Falcon生成 (5文档)")
    print("5. BM25 + 简单生成")
    print("6. BM25 + Falcon生成 (1文档)")
    print("0. 返回主菜单")

    choice = input("\n请选择 (0-6): ").strip()

    config_map = {
        "1": ("faiss", "simple", 1),
        "2": ("faiss", "falcon", 1),
        "3": ("faiss", "falcon", 3),
        "4": ("faiss", "falcon", 5),
        "5": ("bm25", "simple", 1),
        "6": ("bm25", "falcon", 1)
    }

    if choice == "0":
        return
    elif choice in config_map:
        retrieval_method, generation_method, num_docs = config_map[choice]
        run_text_qa(retrieval_method, generation_method, num_docs)
    else:
        print("❌ 无效选择，返回主菜单")

def run_text_qa(retrieval_method: str, generation_method: str, num_docs: int = 1):
    """运行文本问答系统"""
    try:
        from core.modern_rag_system import ModernRAGSystem

        print(f"\n🚀 启动文本问答系统...")
        print(f"   检索方法: {retrieval_method}")
        print(f"   生成方法: {generation_method}")
        if generation_method == "falcon":
            print(f"   文档数量: {num_docs}")

        rag_system = ModernRAGSystem(retrieval_method, generation_method)

        print("\n💡 你可以问关于Romeo和Juliet的任何问题")
        print("例如: 'What metaphor does Romeo use for Juliet?'")
        print("输入 'quit' 退出")

        question_count = 0

        while True:
            question = input(f"\n📝 请输入你的问题: ").strip()

            if question.lower() == 'quit':
                break

            if not question:
                continue

            try:
                # 根据生成方法调用不同的ask方法
                if generation_method == "falcon":
                    result = rag_system.ask(question, k=max(5, num_docs), num_docs=num_docs)
                    print(f"\n🤖 回答 (使用{result.get('num_docs_used', num_docs)}个文档):")
                else:
                    result = rag_system.ask(question)
                    print(f"\n🤖 回答:")

                question_count += 1
                print(f"   {result['answer']}")
                print(f"\n📚 相关段落: {', '.join(result['retrieved_passages'][:3])}")

            except Exception as e:
                print(f"❌ 生成回答时出错: {e}")

        print(f"\n📊 本次会话共回答了 {question_count} 个问题")

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保已安装所需依赖: pip install -r requirements_consolidated.txt")
    except Exception as e:
        print(f"❌ 系统错误: {e}")

def voice_qa_menu():
    """语音问答菜单"""
    print("\n🎤 语音问答系统")
    print("选择配置:")
    print("1. FAISS + 意图模式 (推荐)")
    print("2. FAISS + 简单生成")
    print("3. FAISS + Falcon生成")
    print("4. BM25 + 简单生成")
    print("0. 返回主菜单")

    choice = input("\n请选择 (0-4): ").strip()

    config_map = {
        "1": ("faiss", "intent"),
        "2": ("faiss", "simple"),
        "3": ("faiss", "falcon"),
        "4": ("bm25", "simple")
    }

    if choice == "0":
        return
    elif choice in config_map:
        retrieval_method, generation_method = config_map[choice]
        run_voice_qa(retrieval_method, generation_method)
    else:
        print("❌ 无效选择，返回主菜单")

def run_voice_qa(retrieval_method: str, generation_method: str):
    """运行语音问答系统"""
    try:
        from core.modern_voice_rag_system import ModernVoiceRAGSystem

        print(f"\n🚀 启动语音问答系统...")
        print("⚠️  请确保已连接麦克风和扬声器")

        voice_rag = ModernVoiceRAGSystem(retrieval_method, generation_method)
        voice_rag.interactive_session()

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("语音功能需要额外依赖:")
        print("pip install openai-whisper gTTS sounddevice pygame pydub")
    except Exception as e:
        print(f"❌ 系统错误: {e}")

def run_evaluation():
    """运行性能评估"""
    try:
        print("\n📊 启动性能评估系统...")
        print("这将对比FAISS语义检索和BM25关键词检索的性能")

        import subprocess
        result = subprocess.run([sys.executable, "final_evaluation.py"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ 评估失败: {result.stderr}")

    except Exception as e:
        print(f"❌ 评估错误: {e}")

def run_simple_test():
    """运行简单测试"""
    try:
        print("\n🧪 启动简单测试系统...")
        print("这使用基础的TF-IDF检索方法")

        import subprocess
        result = subprocess.run([sys.executable, "simple_rag_test.py"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ 测试失败: {result.stderr}")

    except Exception as e:
        print(f"❌ 测试错误: {e}")

def system_management_menu():
    """系统管理菜单"""
    print("\n🔧 系统管理")
    print("1. 🔨 构建FAISS索引")
    print("2. 📊 生成意图映射")
    print("3. 🎭 生成Alexa处理器")
    print("4. 🧪 测试Alexa集成")
    print("5. 📦 分析项目依赖")
    print("0. 返回主菜单")

    choice = input("\n请选择 (0-5): ").strip()

    management_scripts = {
        "1": ("modern_faiss_retrieval.py", "构建FAISS索引"),
        "2": ("generate_intent_mapping.py", "生成意图映射"),
        "3": ("generate_alexa_handlers.py", "生成Alexa处理器"),
        "4": ("test_alexa_integration.py", "测试Alexa集成"),
        "5": ("analyze_dependencies.py", "分析项目依赖")
    }

    if choice == "0":
        return
    elif choice in management_scripts:
        script, desc = management_scripts[choice]
        run_management_script(script, desc)
    else:
        print("❌ 无效选择，返回主菜单")

def run_management_script(script: str, description: str):
    """运行管理脚本"""
    try:
        print(f"\n🔧 执行: {description}")

        import subprocess
        result = subprocess.run([sys.executable, script],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ 执行失败: {result.stderr}")

    except Exception as e:
        print(f"❌ 执行错误: {e}")

def show_project_info():
    """显示项目信息"""
    info = """
📖 Romeo & Juliet RAG Question-Answering System

🎯 项目概述:
   基于Walert (CHIIR 2024)现代化改造的文学问答系统
   从RMIT大学FAQ系统升级为Shakespeare文学分析工具

🚀 核心特性:
   • 现代FAISS语义检索 (100%召回率)
   • 传统BM25关键词检索 (93.8%召回率)
   • 混合IB+RAG架构 (意图驱动 + 语义检索)
   • Amazon Alexa语音集成
   • Python 3.12现代技术栈

📊 数据集:
   • 160个Romeo & Juliet文本段落
   • 50个主题，200个问题变体
   • 33个语义化意图映射
   • 完整的评估框架

🛠️ 技术栈:
   • Python 3.12
   • FAISS 1.12.0 (向量检索)
   • sentence-transformers 5.1.1 (文本编码)
   • PyTorch 2.1.0+ (深度学习)
   • OpenAI Whisper (语音识别)
   • gTTS (文本转语音)

🎭 使用场景:
   • 文学教育和研究
   • 语音交互学习
   • 检索技术对比研究
   • 对话AI技术演示

📚 更多信息:
   请查看 README_ROMEO_JULIET.md 和 README_MODERN.md
    """
    print(info)

def check_dependencies():
    """检查依赖包"""
    critical_deps = [
        'pandas', 'numpy', 'scikit-learn', 'torch', 'transformers',
        'faiss', 'sentence_transformers', 'pyserini'
    ]

    optional_deps = {
        'whisper': '语音识别',
        'gtts': '文本转语音',
        'sounddevice': '音频录制',
        'pygame': '音频播放'
    }

    print("\n🔍 依赖检查:")

    missing_critical = []
    for dep in critical_deps:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} (核心依赖)")
            missing_critical.append(dep)

    print(f"\n🔧 可选依赖 (语音功能):")
    for dep, purpose in optional_deps.items():
        try:
            __import__(dep)
            print(f"✅ {dep} - {purpose}")
        except ImportError:
            print(f"⚠️  {dep} - {purpose} (可选)")

    if missing_critical:
        print(f"\n❌ 缺少核心依赖，请安装:")
        print(f"pip install -r requirements_consolidated.txt")
        return False

    return True

def main():
    """主函数"""
    print_banner()

    # 检查依赖
    if not check_dependencies():
        print("\n请先安装必需的依赖包")
        return

    print("\n🎉 系统初始化完成！")

    while True:
        show_main_menu()

        choice = input("\n请选择功能 (0-6): ").strip()

        if choice == "0":
            print("\n👋 感谢使用Romeo & Juliet RAG系统！")
            print("'These violent delights have violent ends.' - 莎士比亚")
            break
        elif choice == "1":
            text_qa_menu()
        elif choice == "2":
            voice_qa_menu()
        elif choice == "3":
            run_evaluation()
        elif choice == "4":
            run_simple_test()
        elif choice == "5":
            system_management_menu()
        elif choice == "6":
            show_project_info()
        else:
            print("❌ 无效选择，请重新输入")

        input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，系统退出")
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
        print("请检查系统配置和依赖包安装")