# Ollama 设置指南

## 1. 安装 Ollama

### Windows
1. 访问 https://ollama.com/download
2. 下载 Windows 安装程序
3. 运行安装程序并完成安装

### Linux/Mac
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## 2. 启动 Ollama

### Windows
- Ollama 安装后会自动在后台运行
- 可以在系统托盘中看到 Ollama 图标
- 如果没有运行，从开始菜单启动 "Ollama"

### Linux/Mac
```bash
ollama serve
```

## 3. 下载模型

在命令行中运行以下命令下载 llama3.2 模型：

```bash
ollama pull llama3.2
```

可选的其他模型：
- `ollama pull mistral` - Mistral 7B (速度快，质量好)
- `ollama pull qwen2.5` - Qwen 2.5 (中文支持好)
- `ollama pull llama3.1` - Llama 3.1 8B (更大的模型)

## 4. 验证安装

运行以下命令验证 Ollama 是否正常工作：

```bash
ollama list
```

应该看到已下载的模型列表。

## 5. 测试集成

在项目目录中运行：

```bash
cd quantitative_eval
python test_ollama_integration.py
```

## 6. 更改模型

如果想使用不同的模型，修改 `app.py` 中的模型名称：

```python
rag_system = IntelligentRAGSystem(use_llm=True, llm_model="mistral")
```

## 故障排除

### 错误: "Failed to connect to Ollama"
- 确保 Ollama 服务正在运行
- Windows: 检查系统托盘中是否有 Ollama 图标
- Linux/Mac: 运行 `ollama serve`

### 错误: "model 'llama3.2' not found"
- 运行 `ollama pull llama3.2` 下载模型

### 响应速度慢
- 考虑使用更小的模型，如 `mistral`
- 或调整 `num_predict` 参数限制响应长度（在 intelligent_rag_system.py 中）

## 当前实现的功能

1. **Known 问题**: 直接返回知识库中的段落，不使用 LLM
2. **Inferred 问题**: 使用 Ollama LLM 整合多个段落生成综合答案
3. **Out-of-KB 问题**: 使用 Ollama LLM 基于一般知识回答问题

这符合论文中描述的 RAG 架构。
