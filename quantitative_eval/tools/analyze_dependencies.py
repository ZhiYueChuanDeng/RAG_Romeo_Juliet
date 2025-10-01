#!/usr/bin/env python3
"""
分析项目中实际使用的依赖包
"""

import os
import re
import ast
from collections import defaultdict

def extract_imports_from_file(file_path):
    """从Python文件中提取import语句"""
    imports = set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析AST来获取import语句
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

        except SyntaxError:
            # 如果AST解析失败，使用正则表达式作为后备
            import_patterns = [
                r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
            ]

            for line in content.split('\n'):
                for pattern in import_patterns:
                    match = re.match(pattern, line.strip())
                    if match:
                        imports.add(match.group(1))

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return imports

def analyze_project_imports():
    """分析项目中所有Python文件的导入"""

    # 定义要分析的文件
    modern_files = [
        'modern_faiss_retrieval.py',
        'modern_rag_system.py',
        'final_evaluation.py',
        'simple_rag_test.py',
        'generate_intent_mapping.py',
        'generate_intent_results.py',
        'generate_alexa_handlers.py',
        'test_alexa_integration.py'
    ]

    # 还要检查data目录下的生成脚本
    data_files = [
        'data/generate_core.py',
        'data/generate_topics.py',
        'data/generate_groundtruth.py',
        'data/generate_gold_summaries.py',
        'data/process_romeo_juliet.py'
    ]

    # src目录下的文件（看看我们是否还需要）
    src_files = [
        'src/retrieval/search.py',
        'src/retrieval/eval.py',
        'src/retrieval/RAG_SYSTEM.py',
        'src/nlg/falcon_gen.py',
        'src/nlg/eval.py'
    ]

    all_imports = defaultdict(list)

    # 分析现代化文件
    print("=== 现代化系统文件导入分析 ===")
    for file_path in modern_files:
        if os.path.exists(file_path):
            imports = extract_imports_from_file(file_path)
            if imports:
                all_imports['modern'].extend(imports)
                print(f"{file_path}: {', '.join(sorted(imports))}")

    # 分析数据生成文件
    print(f"\n=== 数据生成脚本导入分析 ===")
    for file_path in data_files:
        if os.path.exists(file_path):
            imports = extract_imports_from_file(file_path)
            if imports:
                all_imports['data'].extend(imports)
                print(f"{file_path}: {', '.join(sorted(imports))}")

    # 分析原始src文件
    print(f"\n=== 原始src文件导入分析 ===")
    for file_path in src_files:
        if os.path.exists(file_path):
            imports = extract_imports_from_file(file_path)
            if imports:
                all_imports['src'].extend(imports)
                print(f"{file_path}: {', '.join(sorted(imports))}")

    # 统计所有导入
    all_unique_imports = set()
    for category, imports in all_imports.items():
        all_unique_imports.update(imports)

    # 映射到实际的PyPI包名
    package_mapping = {
        'faiss': 'faiss-cpu',
        'sentence_transformers': 'sentence-transformers',
        'sklearn': 'scikit-learn',
        'PIL': 'Pillow',
        'cv2': 'opencv-python',
        'whisper': 'openai-whisper',
        'gtts': 'gTTS',
        'sounddevice': 'sounddevice',
        'scipy': 'scipy',
        'pygame': 'pygame'
    }

    # 过滤掉标准库
    stdlib_modules = {
        'os', 'sys', 'json', 're', 'ast', 'random', 'logging', 'time',
        'threading', 'collections', 'itertools', 'functools', 'pathlib',
        'urllib', 'datetime', 'math', 'io', 'csv', 'pickle', 'copy'
    }

    third_party_packages = set()
    for imp in all_unique_imports:
        if imp not in stdlib_modules:
            package_name = package_mapping.get(imp, imp)
            third_party_packages.add(package_name)

    print(f"\n=== 项目实际使用的第三方包 ===")
    for package in sorted(third_party_packages):
        print(f"  {package}")

    return all_imports, third_party_packages

def compare_with_requirements():
    """对比当前requirements文件"""

    print(f"\n=== 对比现有requirements文件 ===")

    # 读取旧requirements
    old_packages = set()
    try:
        with open('requirements.txt', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    package = line.strip().split('==')[0].split('>=')[0]
                    old_packages.add(package)
    except FileNotFoundError:
        print("requirements.txt not found")

    # 读取新requirements
    new_packages = set()
    try:
        with open('requirements_py312.txt', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    package = line.strip().split('==')[0].split('>=')[0]
                    new_packages.add(package)
    except FileNotFoundError:
        print("requirements_py312.txt not found")

    print(f"旧requirements包数: {len(old_packages)}")
    print(f"新requirements包数: {len(new_packages)}")

    only_in_old = old_packages - new_packages
    only_in_new = new_packages - old_packages

    if only_in_old:
        print(f"\n只在旧requirements中的包:")
        for pkg in sorted(only_in_old):
            print(f"  {pkg}")

    if only_in_new:
        print(f"\n只在新requirements中的包:")
        for pkg in sorted(only_in_new):
            print(f"  {pkg}")

def analyze_src_usage():
    """分析src文件夹的使用情况"""

    print(f"\n=== src文件夹使用分析 ===")

    # 检查现代化文件是否导入src模块
    modern_files = [
        'modern_faiss_retrieval.py',
        'modern_rag_system.py',
        'final_evaluation.py',
        'simple_rag_test.py'
    ]

    imports_src = False
    for file_path in modern_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'from src' in content or 'import src' in content:
                        imports_src = True
                        print(f"{file_path} 导入了src模块")
            except Exception:
                pass

    if not imports_src:
        print("✅ 现代化系统没有导入src模块")
        print("✅ src文件夹可以视为历史代码，保留作为参考")

    # 分析src各模块的作用
    print(f"\nsrc模块功能分析:")
    print("  src/retrieval/search.py - 原始DPR+BM25检索（已被modern_faiss_retrieval.py替代）")
    print("  src/retrieval/RAG_SYSTEM.py - 完整语音RAG系统（包含录音、ASR、TTS）")
    print("  src/nlg/falcon_gen.py - Falcon模型生成（已集成到modern_rag_system.py）")
    print("  src/intent-based/ - Alexa集成（已更新为Romeo & Juliet版本）")

if __name__ == "__main__":
    all_imports, packages = analyze_project_imports()
    compare_with_requirements()
    analyze_src_usage()