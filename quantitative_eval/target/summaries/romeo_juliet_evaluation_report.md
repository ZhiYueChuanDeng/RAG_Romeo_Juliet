# Romeo & Juliet RAG系统评估报告

## 系统概述

本报告总结了Romeo & Juliet RAG系统三种检索方法的性能表现：

1. **FAISS Dense Retrieval**: 基于sentence-transformers的语义检索
2. **BM25 Keyword Search**: 基于关键词的传统检索
3. **Intent-based Retrieval**: 结合意图检测的混合检索

## 评估数据集

- **文档集合**: 160个Romeo & Juliet相关段落
- **查询集合**: 200个问题（涵盖50个主题，每个主题4个变体问题）
- **评估指标**: MAP, NDCG, Precision@K, Recall@K, BPref

## 性能结果

| 方法 | MAP | NDCG | P@5 | P@10 | P@20 | Recall@5 | Recall@10 | Recall@20 | BPref |
|------|-----|------|-----|------|------|----------|-----------|-----------|-------|
| FAISS Dense Retrieval | 0.5531 | 0.6884 | 0.4000 | 0.2750 | 0.1681 | 0.5000 | 0.6875 | 0.8406 | 0.9828 |
| BM25 Keyword Search | 0.3245 | 0.4826 | 0.2225 | 0.1369 | 0.0869 | 0.2781 | 0.3422 | 0.4344 | 0.8766 |
| Intent-based Retrieval | 0.5087 | 0.5826 | 0.4000 | 0.2750 | 0.1375 | 0.5000 | 0.6875 | 0.6875 | 0.6875 |


## 主要发现

### 最佳性能方法
**FAISS Dense Retrieval** 在MAP指标上表现最佳，达到 **0.5531**。

### 方法对比分析

#### FAISS Dense Retrieval
- 优势：在大部分语义相关性指标上表现优秀
- 适用场景：复杂的语义理解查询

#### BM25 Keyword Search
- 优势：计算效率高，对关键词匹配敏感
- 适用场景：精确关键词查询

#### Intent-based Retrieval
- 优势：结合意图理解，平衡准确性和响应速度
- 适用场景：对话式问答系统

## 系统文件结构

```
target/
├── runs/                    # TREC格式检索结果
│   ├── romeo-juliet-faiss.txt
│   ├── romeo-juliet-bm25.txt
│   └── romeo-juliet-intent.txt
├── trec_eval_results/       # 评估结果
│   ├── romeo-juliet-faiss.txt/.tex
│   ├── romeo-juliet-bm25.txt/.tex
│   └── romeo-juliet-intent.txt/.tex
└── summaries/              # 性能总结报告
    ├── romeo_juliet_performance_summary.csv
    └── romeo_juliet_evaluation_report.md
```

## 结论

现代化的Romeo & Juliet RAG系统成功替代了原始RMIT FAQ系统，在保持高精度的同时提供了更好的语义理解能力。FAISS密集检索方法在大多数指标上表现最佳，推荐作为主要的检索方法。

---
*报告生成时间: 2025-10-01 01:13:09*
