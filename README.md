# Lonai

<div align="center">

**🔬 An enterprise-grade intelligent research assistant powered by DeepAgents**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Conduct thorough research on any topic using advanced AI agents with web search capabilities.*

[English](README.md) | [简体中文](README_zh-CN.md)

</div>

---

## ✨ Features

- 🤖 **Powered by DeepAgents**: Leverages LangChain's DeepAgents framework for intelligent research
- 🧠 **Multi-Model Support**: Use OpenAI, DeepSeek, Google Gemini, or Anthropic Claude
- 🔍 **Smart Web Search**: Integrated Tavily API for high-quality search results
- 📋 **Task Management**: Plan, execute, and track multiple research tasks
- 📊 **Multi-Format Export**: Generate reports in Markdown, HTML, or JSON
- 💬 **Interactive CLI**: Beautiful command-line interface with real-time feedback
- 🌐 **Multi-Language**: Support for English and Chinese research
- 💾 **Persistent Storage**: Save and retrieve research history
- ⚙️ **Highly Configurable**: Customize agent behavior, search parameters, and more

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- [Tavily API key](https://tavily.com/) (Required for search)
- One of the following LLM API keys:
  - [Anthropic API key](https://console.anthropic.com/)
  - [OpenAI API key](https://platform.openai.com/)
  - [Google AI Studio Key](https://aistudio.google.com/)
  - Or a DeepSeek/LocalAI endpoint

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd lonai
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

### Configuration Examples (`.env`)

**Anthropic (Default)**:
```bash
TAVILY_API_KEY=tvly-...
ANTHROPIC_API_KEY=sk-ant-...
AGENT_PROVIDER=anthropic
```

**OpenAI / DeepSeek**:
```bash
TAVILY_API_KEY=tvly-...
AGENT_PROVIDER=openai
AGENT_API_KEY=sk-...
AGENT_BASE_URL=https://api.deepseek.com # Optional for custom endpoints
AGENT_MODEL=deepseek-chat
```

## 💡 Usage

### Command Line Interface

1. **Single Research Query**:
   ```bash
   lonai research "What is quantum computing?"
   ```

2. **Chinese Language Support**:
   ```bash
   lonai research "人工智能的最新发展趋势" --lang zh
   ```

3. **Export Report**:
   ```bash
   lonai research "Climate change impacts" --export --format html
   ```

4. **Interactive Chat Mode**:
   ```bash
   lonai chat --interactive
   ```

5. **Batch Research**:
   ```bash
   lonai batch queries.txt
   ```

6. **View History**:
   ```bash
   lonai history --limit 10
   lonai history --search "quantum"
   ```

### Python API

```python
from lonai import ResearchAgent

# Initialize agent
agent = ResearchAgent(language="en")

# Conduct research
result = agent.research(
    query="What are the latest AI developments?",
    save_results=True,
    export_report=True
)

print(result['response'])
```

## 📖 Documentation

### Project Structure

```
lonai/
├── src/lonai/            # Main package
│   ├── core/             # Core agent logic
│   ├── tools/            # Search, storage, export tools
│   ├── config/           # Configuration management
│   ├── cli/              # Command-line interface
│   └── utils/            # Utility functions
├── examples/             # Example scripts
├── docs/                 # Documentation
├── tests/                # Test suite
└── data/                 # Data storage
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `lonai research <query>` | Conduct research on a topic |
| `lonai batch <file>` | Process multiple queries from file |
| `lonai history` | View research history |
| `lonai chat` | Interactive chat mode |
| `lonai config` | Show current configuration |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
