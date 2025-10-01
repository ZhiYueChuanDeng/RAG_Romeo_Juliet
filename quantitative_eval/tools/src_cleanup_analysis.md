# SRC目录清理分析报告

## 📋 总体结论
根据详细分析，**src目录下的绝大部分文件都可以安全删除**，现代化系统已经完全替代了原始功能。只有少数配置文件需要保留。

---

## 🗂️ 文件分类分析

### ✅ **可以删除的Python文件** (共11个)

#### 1. **检索相关文件** - 已被现代系统完全替代
- `src/retrieval/RAG_SYSTEM.py` → 已被 `modern_voice_rag_system.py` 替代
- `src/retrieval/RAG_SYSTEM_BM25.py` → 已被 `modern_voice_rag_system.py` + BM25选项替代
- `src/retrieval/RAG_Voice_Demo.py` → 已被 `modern_voice_rag_system.py` 替代
- `src/retrieval/search.py` → 已被 `modern_faiss_retrieval.py` + `modern_rag_system.py` 替代
- `src/retrieval/eval.py` → 已被 `final_evaluation.py` 替代
- `src/retrieval/build_index.py` → 已被 `modern_faiss_retrieval.py` 的build_index方法替代
- `src/retrieval/helloworld.py` → 测试文件，无实际功能

#### 2. **文本生成相关文件** - 已被增强版本替代
- `src/nlg/falcon_gen.py` → 已被 `modern_rag_system.py` 的完整Falcon集成替代
- `src/nlg/eval.py` → 已被 `final_evaluation.py` 的评估功能替代

#### 3. **数据处理文件** - 功能已整合
- `src/retrieval/data.py` → 数据转换功能已被现代系统内置处理替代

#### 4. **原始Lambda函数** - 已被升级版本替代
- `src/intent-based/lambda/lambda_function.py` → 已被 `lambda_function_complete.py` 替代
- `src/intent-based/lambda/utils.py` → 简单工具函数，现代系统不需要

---

### 🔄 **可以删除的配置文件** (共15个)

#### 1. **旧版Shell脚本** - 已被Python脚本替代
- `src/retrieval/encode.sh` → 已被现代FAISS编码替代
- `src/retrieval/index.sh` → 已被 `modern_faiss_retrieval.py` 替代
- `src/retrieval/index-bm25.sh` → 已被PySerini集成替代
- `src/retrieval/main.sh` → 已被 `main.py` 替代
- `src/retrieval/search.sh` → 已被现代检索系统替代

#### 2. **旧版Alexa模型** - 已被Romeo & Juliet版本替代
- `src/intent-based/interactionModels/custom/en-AU.json`
- `src/intent-based/interactionModels/custom/en-CA.json`
- `src/intent-based/interactionModels/custom/en-GB.json`
- `src/intent-based/interactionModels/custom/en-IN.json`
- `src/intent-based/interactionModels/custom/en-US.json`
(这些都是RMIT版本，已被Romeo & Juliet版本替代)

#### 3. **过时的文档和配置**
- `src/retrieval/README.md` → 已过时
- `src/README.md` → 已过时
- `src/intent-based/README` → 已过时
- `src/intent-based/lambda/requirements.txt` → 已被整合到主requirements中
- `src/nlg/rag-dense.Rproj` → R项目文件，不需要
- `src/nlg/end2end_eval.R` → R脚本，已被Python评估替代
- `src/.DS_Store` → 系统文件

---

### 🔒 **需要保留的文件** (共4个)

#### 1. **现代Alexa集成** (必须保留)
- ✅ `src/intent-based/lambda/lambda_function_complete.py` - 完整的RMIT意图处理
- ✅ `src/intent-based/lambda/lambda_function_romeo_juliet.py` - Romeo & Juliet专用版本
- ✅ `src/intent-based/interactionModels/custom/en-US-complete.json` - 完整意图模型
- ✅ `src/intent-based/interactionModels/custom/en-US-romeo-juliet.json` - Romeo & Juliet意图模型

#### 2. **参考文档** (建议保留)
- ✅ `src/nlg/falcon_details.txt` - Falcon模型配置参考
- ✅ `src/intent-based/skill.json` - Alexa技能配置

---

## 🎯 **清理建议**

### 方案1: 完全清理 (推荐)
```bash
# 删除所有旧文件，只保留现代Alexa集成
rm -rf src/retrieval/
rm -rf src/nlg/
rm -f src/intent-based/lambda/lambda_function.py
rm -f src/intent-based/lambda/utils.py
rm -f src/intent-based/interactionModels/custom/en-*.json
# 保留 lambda_function_complete.py, lambda_function_romeo_juliet.py 等现代文件
```

### 方案2: 保守清理
```bash
# 重命名src为src_legacy作为备份
mv src src_legacy
# 只保留必要的Alexa文件
mkdir -p src/intent-based/lambda/
mkdir -p src/intent-based/interactionModels/custom/
# 复制现代文件到新的src目录
```

---

## 📊 **清理统计**

- **总文件数**: 30个
- **可删除**: 26个 (86.7%)
- **需保留**: 4个 (13.3%)
- **空间节省**: 预计节省 80%+ 的src目录空间

---

## ⚠️ **注意事项**

1. **Alexa集成文件必须保留**: 这些是系统的重要组成部分
2. **建议先备份**: 执行清理前建议先备份整个src目录
3. **测试验证**: 清理后运行完整系统测试确保功能正常
4. **文档更新**: 清理后需要更新相关文档中的文件路径引用

---

## 🏆 **清理后的优势**

1. **代码库简化**: 移除冗余和过时代码
2. **维护性提升**: 减少混淆，专注现代系统
3. **存储优化**: 显著减少磁盘空间占用
4. **开发效率**: 减少无关文件干扰，提升开发体验