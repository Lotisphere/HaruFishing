<div align="center">

# HaruFishing 🎀

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Gemini API](https://img.shields.io/badge/Gemini-Pro%2FFlash-8E75B2.svg)](https://aistudio.google.com/)

一个极简主义的多智能体（Multi-Agent）社交圈层推演与预测引擎。
*预测每一次吃瓜事件的蝴蝶效应，让智能体为你演绎。*

[English](./README.md) | [中文介绍](./README_ZH.md)

</div>

## 📖 什么是 HaruFishing？

HaruFishing 是一个受 MiroFish 等项目启发的轻量级群体智能沙盘。你可以输入一个触发事件和一组人物卡片（包括性格、背景和人际关系），系统会自动生成具备自主意识的 AI 智能体来扮演这些角色。它们会在回合制的“黑板”环境中互动，并动态生成一张展示心理博弈和行动的力导向知识图谱（Knowledge Graph）。

**核心应用场景：**
- 🎭 **故事编剧推演：** 预测你的角色对意外剧情会作何反应。
- 🏢 **职场政治模拟：** 分析公司突发事件可能引发的连锁反应。
- 🍉 **八卦吃瓜沙盘：** 投喂聊天记录、新闻或 PDF 文档，看戏如何收场。

## 🚀 快速开始

### 运行要求
- Python 3.10 或更高版本。
- 一个免费的 [Google Gemini API Key](https://aistudio.google.com/)。

### 选项 A：一键全自动启动 (Windows)
我们提供了一个自动化的批处理脚本，实现无缝、零配置的启动体验：
1. 双击运行 `启动_HaruFishing.bat`。
2. 按照屏幕提示 (Y/N) 自动安装 Python（如果缺失）以及所有必需的依赖库。
3. Web UI 会在你的默认浏览器中自动打开。

### 选项 B：手动运行
```bash
# 1. 克隆或进入项目目录
cd D:\HaruFishing

# 2. 安装依赖
python -m pip install -r requirements.txt

# 3. 配置你的 API Key（或者稍后直接在 Web UI 中输入）
echo GEMINI_API_KEY=在这里填入你的API_KEY > .env

# 4. 启动 Web 界面
python -m streamlit run ui/web_app.py
```

## 🏗️ 架构与核心模块

HaruFishing 采用了完全解耦的三模块架构，确保了极低的 Token 消耗、高确定性的输出以及强大的容错能力。

*   **模块 A: 剧本解析器 (`core/ingestion.py`)**
    *   **文档解析：** 使用 `pypdf` 和 `python-docx` 从 `.txt`, `.pdf`, 或 `.docx` 中提取纯文本。
    *   **AI 提炼引擎：** 严格使用 Gemini 的 JSON 模式，从长文本中全自动提炼核心事件、角色性格和人物关系。
    *   **提示词构建：** 将提取的数据转化为强大的 System Prompts (`config/prompts.py`)。
*   **模块 B: 核心推演引擎 (`core/engine.py`)**
    *   **黑板系统：** 智能体在一个共享的上下文黑板上轮流对不断发展的局势做出反应。
    *   **增量图谱构建：** 智能体在每个回合结束时输出结构化的 JSON，动态构建节点和连线，大幅节省 Token。
    *   **极致容错：** 摒弃官方 SDK，使用带 60 秒超时控制的原生 HTTP 请求防止死锁，并结合 `tenacity` 实现针对 API 限流 (429) 的指数退避重试。
*   **模块 C: 裁判生成器 (`core/synthesizer.py`)**
    *   **日志总结：** 一个不参与角色扮演的“上帝视角”智能体（The Observer）读取交互日志，并预测 3 个近期可能的结局及概率。
    *   **Token 优化：** 自动截断超长日志，防止超出上下文窗口限制。

## 🌐 可视化与 UI
前端基于 **Streamlit** (`ui/web_app.py`) 构建，包含以下特色：
- **双语界面：** 瞬间无缝切换 English 和 中文。
- **双模式输入：** 可以一键运行自带的经典“奔驰事件”案例，也可以拖拽上传自己的吃瓜文档进行自定义提炼。
- **动态知识图谱：** 深度集成了 **Pyvis** 以渲染实时的力导向网络图。你可以用鼠标自由拖拽节点（人物、事件、动作），直观地感受错综复杂的关系网！

## ⚙️ 依赖清单概览
- `google-generativeai`: 核心大模型交互。
- `pydantic`: 严格的数据 Schema 和 JSON 校验。
- `streamlit`: Web 应用框架。
- `pyvis`: 交互式网络图谱渲染。
- `tenacity`: 强大的容错重试逻辑。
- `pypdf` & `python-docx`: 强大的文档解析能力。

---
*Made with 🎀 by Haru & Mangolotis-anon*
