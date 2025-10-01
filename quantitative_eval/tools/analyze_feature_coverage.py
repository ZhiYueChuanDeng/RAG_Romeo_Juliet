#!/usr/bin/env python3
"""
详细的功能覆盖分析
对比src/下的原始功能与现代化系统的功能覆盖情况
"""

import os
import ast
import inspect
from typing import Dict, List, Any

def analyze_file_functions(file_path: str) -> Dict[str, Any]:
    """分析Python文件中的函数和类"""
    result = {
        "file": file_path,
        "functions": [],
        "classes": [],
        "imports": [],
        "main_purpose": "",
        "key_features": []
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析AST
        tree = ast.parse(content)

        # 提取函数
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                result["functions"].append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args]
                })
            elif isinstance(node, ast.ClassDef):
                result["classes"].append({
                    "name": node.name,
                    "line": node.lineno
                })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result["imports"].append(node.module)

        # 分析主要用途（通过注释和函数名）
        if "whisper" in content or "sounddevice" in content:
            result["key_features"].append("语音处理")
        if "Falcon" in content or "falcon" in content:
            result["key_features"].append("Falcon模型")
        if "pipeline" in content and "transformers" in content:
            result["key_features"].append("文本生成")
        if "FaissSearcher" in content or "LuceneSearcher" in content:
            result["key_features"].append("检索功能")
        if "lambda" in file_path:
            result["key_features"].append("AWS Lambda")
        if "eval" in file_path:
            result["key_features"].append("评估功能")

    except Exception as e:
        result["error"] = str(e)

    return result

def analyze_src_structure():
    """分析src文件夹结构和功能"""

    src_analysis = {}

    # 定义src下的主要文件
    src_files = [
        "src/retrieval/RAG_SYSTEM.py",
        "src/retrieval/RAG_SYSTEM_BM25.py",
        "src/retrieval/RAG_Voice_Demo.py",
        "src/retrieval/search.py",
        "src/retrieval/eval.py",
        "src/retrieval/build_index.py",
        "src/retrieval/data.py",
        "src/retrieval/helloworld.py",
        "src/nlg/falcon_gen.py",
        "src/nlg/eval.py",
        "src/intent-based/lambda/lambda_function.py",
        "src/intent-based/lambda/utils.py"
    ]

    print("=== 原始src系统功能分析 ===")

    for file_path in src_files:
        if os.path.exists(file_path):
            analysis = analyze_file_functions(file_path)
            src_analysis[file_path] = analysis

            print(f"\n📁 {file_path}:")
            if analysis.get("key_features"):
                print(f"   核心功能: {', '.join(analysis['key_features'])}")
            print(f"   函数数量: {len(analysis['functions'])}")
            print(f"   类数量: {len(analysis['classes'])}")

            # 显示关键函数
            key_functions = [f for f in analysis['functions'] if not f['name'].startswith('_')][:5]
            if key_functions:
                print(f"   关键函数: {', '.join([f['name'] for f in key_functions])}")

    return src_analysis

def compare_with_modern_system():
    """对比现代化系统的功能覆盖"""

    print(f"\n=== 功能覆盖对比分析 ===")

    # 定义功能映射关系
    feature_mapping = {
        "src/retrieval/RAG_SYSTEM.py": {
            "modern_equivalent": "modern_voice_rag_system.py",
            "coverage_status": "需要验证",
            "original_features": [
                "完整语音RAG流程",
                "语音录制 (sounddevice)",
                "语音转文字 (whisper)",
                "DPR密集检索",
                "Falcon文本生成",
                "文字转语音 (gTTS)",
                "音频播放 (pygame)",
                "日志记录",
                "回调函数处理"
            ]
        },
        "src/retrieval/RAG_SYSTEM_BM25.py": {
            "modern_equivalent": "modern_voice_rag_system.py + modern_rag_system.py (BM25)",
            "coverage_status": "需要验证",
            "original_features": [
                "BM25版本语音RAG",
                "传统关键词检索"
            ]
        },
        "src/retrieval/search.py": {
            "modern_equivalent": "modern_faiss_retrieval.py + modern_rag_system.py",
            "coverage_status": "已覆盖",
            "original_features": [
                "DPR密集检索",
                "BM25检索",
                "TREC格式输出",
                "批量查询处理"
            ]
        },
        "src/retrieval/eval.py": {
            "modern_equivalent": "final_evaluation.py",
            "coverage_status": "已覆盖",
            "original_features": [
                "检索性能评估",
                "RANX评估工具",
                "TREC评估"
            ]
        },
        "src/retrieval/build_index.py": {
            "modern_equivalent": "modern_faiss_retrieval.py (build_index方法)",
            "coverage_status": "已覆盖",
            "original_features": [
                "FAISS索引构建"
            ]
        },
        "src/nlg/falcon_gen.py": {
            "modern_equivalent": "modern_rag_system.py (_generate_with_falcon方法)",
            "coverage_status": "已覆盖",
            "original_features": [
                "Falcon-7B模型加载",
                "文本生成pipeline",
                "多种生成函数变体",
                "生成参数配置"
            ]
        },
        "src/nlg/eval.py": {
            "modern_equivalent": "final_evaluation.py",
            "coverage_status": "已覆盖",
            "original_features": [
                "ROUGE评估",
                "BERTScore评估",
                "文本生成质量评估"
            ]
        },
        "src/intent-based/lambda/lambda_function.py": {
            "modern_equivalent": "src/intent-based/lambda/lambda_function_complete.py",
            "coverage_status": "已升级",
            "original_features": [
                "40+个RMIT意图处理器",
                "AWS Lambda处理",
                "Alexa Skills Kit集成"
            ]
        }
    }

    coverage_summary = {
        "完全覆盖": [],
        "部分覆盖": [],
        "需要增强": [],
        "缺失功能": []
    }

    for src_file, mapping in feature_mapping.items():
        print(f"\n🔍 {src_file}")
        print(f"   现代对应: {mapping['modern_equivalent']}")
        print(f"   状态: {mapping['coverage_status']}")
        print(f"   原功能:")
        for feature in mapping['original_features']:
            print(f"     - {feature}")

        # 分类
        if mapping['coverage_status'] == "已覆盖":
            coverage_summary["完全覆盖"].append(src_file)
        elif mapping['coverage_status'] == "部分覆盖":
            coverage_summary["部分覆盖"].append(src_file)
        elif mapping['coverage_status'] == "需要验证":
            coverage_summary["需要增强"].append(src_file)
        else:
            coverage_summary["缺失功能"].append(src_file)

    return coverage_summary

def detailed_falcon_comparison():
    """详细对比Falcon功能"""

    print(f"\n=== Falcon功能详细对比 ===")

    print("📊 src/nlg/falcon_gen.py 原始功能:")

    try:
        with open("src/nlg/falcon_gen.py", 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取函数定义
        import re
        functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):', content)
        print(f"   原始函数: {', '.join(functions)}")

        # 检查关键配置
        if "gen_answer_base1_v1" in content:
            print("   ✅ 基础生成函数")
        if "pipeline" in content:
            print("   ✅ Transformers pipeline")
        if "max_new_tokens" in content:
            print("   ✅ 生成参数配置")
        if "temperature" in content:
            print("   ✅ 温度参数")

    except FileNotFoundError:
        print("   ❌ 原文件不存在")

    print(f"\n📊 modern_rag_system.py 现代功能:")

    try:
        with open("modern_rag_system.py", 'r', encoding='utf-8') as f:
            content = f.read()

        if "_generate_with_falcon" in content:
            print("   ✅ Falcon生成方法")
        if "AutoModelForCausalLM" in content:
            print("   ✅ 模型加载")
        if "generate(" in content:
            print("   ✅ 生成调用")
        if "temperature" in content:
            print("   ✅ 生成参数")

        # 检查是否缺少原始功能
        missing_features = []

        if "_gen_answer_base1_v1" not in content:
            missing_features.append("原始生成函数变体")
        if "Generate an answer to be synthesized" not in content:
            missing_features.append("原始提示模板")

        if missing_features:
            print("   ⚠️  缺少功能:")
            for feature in missing_features:
                print(f"     - {feature}")
        else:
            print("   ✅ 所有原始功能已完整集成")

    except FileNotFoundError:
        print("   ❌ 现代文件不存在")

def identify_enhancement_needs():
    """识别需要增强的功能"""

    print(f"\n=== 功能增强需求分析 ===")

    enhancement_needs = [
        {
            "area": "Falcon文本生成",
            "issue": "modern_rag_system.py的Falcon集成可能不完整",
            "action": "增强_generate_with_falcon方法，包含原始的所有生成变体",
            "priority": "高"
        },
        {
            "area": "语音RAG系统",
            "issue": "需要验证modern_voice_rag_system.py是否完全替代RAG_SYSTEM.py",
            "action": "详细对比语音流程的每个步骤",
            "priority": "高"
        },
        {
            "area": "评估功能",
            "issue": "src/nlg/eval.py的ROUGE和BERTScore评估",
            "action": "在final_evaluation.py中添加文本生成质量评估",
            "priority": "中"
        },
        {
            "area": "索引构建",
            "issue": "build_index.py的所有功能是否完全迁移",
            "action": "验证modern_faiss_retrieval.py的索引构建完整性",
            "priority": "中"
        },
        {
            "area": "数据处理",
            "issue": "src/retrieval/data.py的数据处理工具",
            "action": "检查是否需要独立的数据处理模块",
            "priority": "低"
        }
    ]

    for need in enhancement_needs:
        print(f"\n🔧 {need['area']} ({need['priority']}优先级)")
        print(f"   问题: {need['issue']}")
        print(f"   行动: {need['action']}")

    return enhancement_needs

def main():
    """主分析函数"""

    print("🔍 Romeo & Juliet RAG系统 - 功能覆盖完整性分析")
    print("=" * 70)

    # 分析src结构
    src_analysis = analyze_src_structure()

    # 功能覆盖对比
    coverage_summary = compare_with_modern_system()

    # Falcon详细对比
    detailed_falcon_comparison()

    # 增强需求
    enhancement_needs = identify_enhancement_needs()

    # 总结
    print(f"\n" + "=" * 70)
    print(f"📋 分析总结:")

    for category, files in coverage_summary.items():
        if files:
            print(f"\n{category}: {len(files)} 个文件")
            for file in files:
                print(f"  - {file}")

    print(f"\n🎯 建议的下一步行动:")
    print(f"1. 增强Falcon集成功能 (高优先级)")
    print(f"2. 验证语音RAG完整性 (高优先级)")
    print(f"3. 补充文本生成评估 (中优先级)")
    print(f"4. 完善数据处理工具 (低优先级)")

if __name__ == "__main__":
    main()