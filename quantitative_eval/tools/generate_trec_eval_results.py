#!/usr/bin/env python3
"""
为Romeo & Juliet RAG系统生成trec_eval评估结果
使用新生成的runs文件和qrels文件
"""

import os
import subprocess
import shutil
from pathlib import Path

def run_trec_eval(qrels_file: str, runs_file: str, output_file: str):
    """
    运行trec_eval程序生成评估结果

    Args:
        qrels_file: 相关性判断文件路径
        runs_file: 检索结果文件路径
        output_file: 输出结果文件路径
    """

    try:
        # 检查trec_eval程序是否存在
        trec_eval_cmd = "trec_eval"

        # 运行trec_eval命令
        cmd = [trec_eval_cmd, "-m", "all_trec", qrels_file, runs_file]

        print(f"运行命令: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if result.returncode == 0:
            # 保存结果
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            print(f"评估结果保存到: {output_file}")
            return True
        else:
            print(f"trec_eval执行失败: {result.stderr}")
            return False

    except FileNotFoundError:
        print("❌ trec_eval程序未找到，请确保已安装")
        print("提示：可以从 https://github.com/usnistgov/trec_eval 下载")
        return False
    except Exception as e:
        print(f"运行trec_eval时出错: {e}")
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

    # 读取关键指标
    metrics = {}

    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[1] == "all":
                metric_name = parts[0]
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

    # 添加主要指标
    key_metrics = {
        'map': 'MAP',
        'P_5': 'P@5',
        'P_10': 'P@10',
        'P_20': 'P@20',
        'recall_5': 'Recall@5',
        'recall_10': 'Recall@10',
        'recall_20': 'Recall@20',
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
    print("🎭 生成Romeo & Juliet RAG系统trec_eval评估结果")
    print("=" * 60)

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

        print(f"\\n=== 处理 {method_name} ===")

        if not os.path.exists(runs_file):
            print(f"⚠️  runs文件不存在: {runs_file}")
            continue

        # 生成trec_eval结果
        if run_trec_eval(qrels_file, runs_file, output_txt):
            # 生成LaTeX摘要
            generate_tex_summary(output_txt, output_tex, method_name)
            success_count += 1
        else:
            print(f"❌ {method_name} 评估失败")

    print(f"\\n✅ 完成！成功生成了 {success_count}/{len(runs_configs)} 个评估结果")

    # 显示结果文件
    results_dir = "target/trec_eval_results"
    if os.path.exists(results_dir):
        print(f"\\n📊 生成的评估结果文件:")
        for filename in sorted(os.listdir(results_dir)):
            filepath = os.path.join(results_dir, filename)
            if os.path.isfile(filepath):
                file_size = os.path.getsize(filepath)
                print(f"  {filename}: {file_size} bytes")

    if success_count == 0:
        print("\\n💡 提示：如果trec_eval未安装，你可以：")
        print("  1. 下载安装：https://github.com/usnistgov/trec_eval")
        print("  2. 或使用pytrec_eval包：pip install pytrec_eval")

if __name__ == "__main__":
    main()