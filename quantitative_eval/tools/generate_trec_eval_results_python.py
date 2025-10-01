#!/usr/bin/env python3
"""
为Romeo & Juliet RAG系统生成trec_eval评估结果 - Python版本
使用pytrec_eval库进行评估
"""

import os
import shutil
import pytrec_eval
from collections import defaultdict

def load_qrels(qrels_file: str):
    """
    加载qrels文件

    Args:
        qrels_file: qrels文件路径

    Returns:
        dict: 查询相关性判断字典
    """
    qrels = defaultdict(dict)

    with open(qrels_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                query_id = parts[0]
                doc_id = parts[2]
                relevance = int(parts[3])
                qrels[query_id][doc_id] = relevance

    return dict(qrels)

def load_runs(runs_file: str):
    """
    加载runs文件

    Args:
        runs_file: runs文件路径

    Returns:
        dict: 检索结果字典
    """
    runs = defaultdict(dict)

    with open(runs_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 6:
                query_id = parts[0]
                doc_id = parts[2]
                score = float(parts[4])
                runs[query_id][doc_id] = score

    return dict(runs)

def run_pytrec_eval(qrels_file: str, runs_file: str, output_file: str):
    """
    使用pytrec_eval进行评估

    Args:
        qrels_file: 相关性判断文件路径
        runs_file: 检索结果文件路径
        output_file: 输出结果文件路径

    Returns:
        bool: 是否成功
    """
    try:
        print(f"加载qrels: {qrels_file}")
        qrels = load_qrels(qrels_file)
        print(f"查询数量: {len(qrels)}")

        print(f"加载runs: {runs_file}")
        runs = load_runs(runs_file)
        print(f"查询数量: {len(runs)}")

        # 创建评估器 - 使用P@4和Recall@4更符合实际（每个topic对应4个段落）
        evaluator = pytrec_eval.RelevanceEvaluator(
            qrels,
            {'map', 'ndcg', 'P_4', 'P_10', 'recall_4', 'recall_10', 'bpref'}
        )

        # 运行评估
        results = evaluator.evaluate(runs)

        # 格式化输出
        output_lines = []

        # 计算总体平均值
        all_metrics = defaultdict(list)
        for query_id, query_results in results.items():
            for metric, value in query_results.items():
                all_metrics[metric].append(value)

        # 先输出每个查询的结果
        for query_id in sorted(results.keys()):
            query_results = results[query_id]
            for metric in sorted(query_results.keys()):
                value = query_results[metric]
                output_lines.append(f"{metric:<20}\t{query_id}\t{value:.4f}")

        # 输出总体平均值
        output_lines.append("")  # 空行分隔
        for metric in sorted(all_metrics.keys()):
            values = all_metrics[metric]
            avg_value = sum(values) / len(values) if values else 0.0
            output_lines.append(f"{metric:<20}\tall\t{avg_value:.4f}")

        # 保存结果
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))

        print(f"评估结果保存到: {output_file}")

        # 显示关键指标
        print("关键指标 (平均值):")
        key_metrics = ['map', 'ndcg', 'P_4', 'recall_4', 'bpref']
        for metric in key_metrics:
            if metric in all_metrics:
                values = all_metrics[metric]
                avg_value = sum(values) / len(values)
                print(f"  {metric.upper()}: {avg_value:.4f}")

        return True

    except Exception as e:
        print(f"评估过程中出错: {e}")
        return False

def generate_tex_summary(txt_file: str, tex_file: str, method_name: str):
    """
    生成LaTeX格式的评估摘要

    Args:
        txt_file: trec_eval文本结果文件
        tex_file: 输出LaTeX文件路径
        method_name: 方法名称
    """
    if not os.path.exists(txt_file):
        print(f"❌ 文本结果文件不存在: {txt_file}")
        return

    # 读取平均值指标
    metrics = {}

    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3 and parts[1] == "all":
                metric_name = parts[0].strip()
                value = parts[2]
                metrics[metric_name] = value

    # 生成LaTeX表格
    latex_content = f"""% Romeo & Juliet RAG System - {method_name} 评估结果
\\begin{{table}}[h]
\\centering
\\caption{{{method_name} 方法评估结果}}
\\begin{{tabular}}{{|l|c|}}
\\hline
指标 & 值 \\\\
\\hline
"""

    # 添加主要指标（使用P@4和Recall@4更符合实际）
    key_metrics = {
        'map': 'MAP',
        'P_4': 'P@4',
        'P_10': 'P@10',
        'recall_4': 'Recall@4',
        'recall_10': 'Recall@10',
        'ndcg': 'NDCG',
        'bpref': 'BPref'
    }

    for metric_key, metric_label in key_metrics.items():
        if metric_key in metrics:
            latex_content += f"{metric_label} & {metrics[metric_key]} \\\\\n"

    latex_content += """\\hline
\\end{tabular}
\\end{table}
"""

    # 保存LaTeX文件
    os.makedirs(os.path.dirname(tex_file), exist_ok=True)
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)

    print(f"LaTeX摘要保存到: {tex_file}")

def clear_old_results():
    """清理旧的RMIT相关评估结果"""
    results_dir = "target/trec_eval_results"

    if not os.path.exists(results_dir):
        print("trec_eval_results目录不存在，跳过清理")
        return

    print("=== 清理旧的RMIT评估结果 ===")

    # 备份旧文件
    backup_dir = "target/trec_eval_results_backup_rmit"
    if os.path.exists(results_dir):
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        shutil.copytree(results_dir, backup_dir)
        print(f"旧文件已备份到: {backup_dir}")

    # 清空目录
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    os.makedirs(results_dir, exist_ok=True)

    print("旧评估结果已清理")

def main():
    """主函数"""
    print("🎭 生成Romeo & Juliet RAG系统trec_eval评估结果 (Python版)")
    print("=" * 65)

    # 确保在正确的目录中
    if not os.path.exists("data/qrels.txt"):
        print("❌ 请在quantitative_eval目录中运行此脚本")
        return

    # 清理旧结果
    clear_old_results()

    # 文件路径配置
    qrels_file = "data/qrels.txt"
    runs_configs = [
        {
            "runs_file": "target/runs/romeo-juliet-faiss.txt",
            "output_txt": "target/trec_eval_results/romeo-juliet-faiss.txt",
            "output_tex": "target/trec_eval_results/romeo-juliet-faiss.tex",
            "method_name": "FAISS Dense Retrieval"
        },
        {
            "runs_file": "target/runs/romeo-juliet-bm25.txt",
            "output_txt": "target/trec_eval_results/romeo-juliet-bm25.txt",
            "output_tex": "target/trec_eval_results/romeo-juliet-bm25.tex",
            "method_name": "BM25 Keyword Search"
        },
        {
            "runs_file": "target/runs/romeo-juliet-intent.txt",
            "output_txt": "target/trec_eval_results/romeo-juliet-intent.txt",
            "output_tex": "target/trec_eval_results/romeo-juliet-intent.tex",
            "method_name": "Intent-based Retrieval"
        }
    ]

    success_count = 0

    for config in runs_configs:
        runs_file = config["runs_file"]
        output_txt = config["output_txt"]
        output_tex = config["output_tex"]
        method_name = config["method_name"]

        print(f"\n=== 处理 {method_name} ===")

        if not os.path.exists(runs_file):
            print(f"⚠️  runs文件不存在: {runs_file}")
            continue

        # 生成trec_eval结果
        if run_pytrec_eval(qrels_file, runs_file, output_txt):
            # 生成LaTeX摘要
            generate_tex_summary(output_txt, output_tex, method_name)
            success_count += 1
        else:
            print(f"❌ {method_name} 评估失败")

    print(f"\n✅ 完成！成功生成了 {success_count}/{len(runs_configs)} 个评估结果")

    # 显示结果文件
    results_dir = "target/trec_eval_results"
    if os.path.exists(results_dir):
        print(f"\n📊 生成的评估结果文件:")
        for filename in sorted(os.listdir(results_dir)):
            filepath = os.path.join(results_dir, filename)
            if os.path.isfile(filepath):
                file_size = os.path.getsize(filepath)
                print(f"  {filename}: {file_size} bytes")

if __name__ == "__main__":
    main()