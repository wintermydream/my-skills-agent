# My Skills Agent 🚀

这是一个基于国产大模型（智谱GLM、通义千问）和 OpenRouter 的智能 Agent 框架。它支持通过 Markdown 文件定义“技能”（Skills），并根据用户输入自动匹配并执行相应的任务。

## 🌟 核心特性

- **多模型支持**：动态切换智谱 GLM、通义千问、OpenRouter (Claude/Llama 等)。
- **技能系统**：通过简单的 Markdown + YAML 配置定义复杂指令。
- **递归引用**：技能之间可以相互引用，支持模块化指令编写。
- **智能缓存**：内置请求缓存机制，节省 API 消耗并提升响应速度。
- **易于扩展**：添加新功能只需在 `skills/` 目录下创建一个新的文件夹和 `SKILL.md`。

## 🛠️ 快速开始

### 1. 安装依赖

```bash
pip install pyyaml zhipuai dashscope openai
```

### 2. 配置 API Key

将项目根目录下的 `config.yaml.template` 重命名为 `config.yaml`，并填写你的 API 密钥：

```yaml
api_keys:
  zhipu: "你的智谱API密钥"
  qwen: "你的通义千问API密钥"
  openrouter: "你的OpenRouter API密钥"

default_model: mimo-v2-flash # 默认使用的模型
```

### 3. 定义一个技能

在 `skills/` 目录下创建一个新目录（例如 `translator`），并添加 `SKILL.md`：

```markdown
---
name: "专业翻译官"
triggers: ["翻译", "translate"]
model_preference: "claude-3.5-haiku"
---
你是一个专业的翻译官，请将以下文本翻译成中文，保持语气自然、地道。
```

## 💻 使用示例

你可以直接在 Python 中调用 `SkillsAgent`：

```python
from agent import SkillsAgent

# 初始化 Agent
agent = SkillsAgent()

# 示例 1：触发翻译技能
query = "请帮我翻译：Artificial Intelligence is changing the world."
result = agent.process(query)
print(result)

# 示例 2：普通对话（未匹配到特定技能时使用默认模型）
query = "你好，今天天气怎么样？"
result = agent.process(query)
print(result)
```

## 📂 项目结构

- `agent.py`: 核心逻辑实现。
- `config.yaml`: 配置文件（包含 API 密钥和模型设置）。
- `skills/`: 存放所有技能定义的目录。
- `scripts/`: 包含一些实用的测试和检查脚本。

## 📄 开源协议

MIT License
