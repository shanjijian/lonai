# Lonai

<div align="center">

**🔬 基于 DeepAgents 构建的企业级智能研究助手**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*利用先进的 AI 智能体和网络搜索能力，对任何主题进行深入研究。*

[English](README.md) | [简体中文](README_zh-CN.md)

</div>

---

## ✨ 核心特性

- 🤖 **DeepAgents 驱动**：利用 LangChain 的 DeepAgents 框架进行智能研究规划
- 🧠 **多模型支持**：支持 OpenAI, DeepSeek, Google Gemini, 或 Anthropic Claude
- 🔍 **智能网络搜索**：集成 Tavily API 提供高质量搜索结果
- 📋 **任务管理**：自动规划、执行和追踪多个研究子任务
- 📊 **多格式导出**：生成 Markdown, HTML, 或 JSON 格式的精美报告
- 💬 **交互式 CLI**：现代化命令行界面，提供实时进度反馈
- 🌐 **多语言支持**：原生支持中文和英文研究
- 💾 **持久化存储**：自动保存并可随时检索历史研究记录
- ⚙️ **高度可配置**：自定义 Agent 行为、搜索参数和 Prompt

## 🚀 快速开始

### 前置要求

- Python 3.9 或更高版本
- [Tavily API key](https://tavily.com/) (搜索必备)
- 以下任一 LLM API Key:
  - [Anthropic API key](https://console.anthropic.com/)
  - [OpenAI API key](https://platform.openai.com/)
  - [Google AI Studio Key](https://aistudio.google.com/)
  - 或者 DeepSeek / LocalAI 等兼容接口

### 安装步骤

1. **克隆项目**:
   ```bash
   git clone https://github.com/shanjijian/lonai
   cd lonai
   ```

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **安装包 (开发模式)**:
   ```bash
   pip install -e .
   ```

4. **配置环境变量**:
   ```bash
   cp .env.example .env
   # 编辑 .env 文件填入你的 API Key
   ```

### 配置示例 (`.env`)

**DeepSeek (推荐/示例)**:
```bash
TAVILY_API_KEY=tvly-your-key
AGENT_PROVIDER=openai           # DeepSeek 兼容 OpenAI 协议
AGENT_API_KEY=sk-your-deepseek-key
AGENT_BASE_URL=https://api.deepseek.com
AGENT_MODEL=deepseek-chat
```

**OpenAI**:
```bash
TAVILY_API_KEY=tvly-your-key
AGENT_PROVIDER=openai
AGENT_API_KEY=sk-your-openai-key
AGENT_MODEL=gpt-4-turbo
```

## 💡 使用指南

### 命令行工具 (CLI)

1. **单次研究**:
   ```bash
   lonai research "量子计算的未来"
   ```

2. **指定中文语言**:
   ```bash
   lonai research "2024年人工智能发展趋势" --lang zh
   ```

3. **导出 HTML 报告**:
   ```bash
   lonai research "气候变化的影响" --export --format html
   ```

4. **交互式对话模式**:
   ```bash
   lonai chat --interactive
   ```

5. **查看历史记录**:
   ```bash
   lonai history --limit 10
   ```

### Python API 调用

```python
from lonai import ResearchAgent

# 初始化 Agent
agent = ResearchAgent(language="zh")

# 执行研究
result = agent.research(
    query="生成式 AI 在医疗领域的应用",
    save_results=True,
    export_report=True
)

print(result['response'])
```

## 📖 项目结构

```
lonai/
├── src/lonai/            # 主包
│   ├── core/             # Agent 核心逻辑
│   ├── tools/            # 搜索、存储、导出工具
│   ├── config/           # 配置管理
│   ├── cli/              # 命令行界面
│   └── utils/            # 工具函数
├── examples/             # 示例脚本
├── docs/                 # 详细文档
└── data/                 # 数据存储目录
```

## 🤝 贡献

欢迎提交 Pull Request 或 Issue！

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。
