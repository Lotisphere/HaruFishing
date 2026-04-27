<div align="center">

# HaruFishing 🎀
<img src="./assets/cat.png" width="150" alt="Running Cat" />


[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Gemini API](https://img.shields.io/badge/Gemini-Pro%2FFlash-8E75B2.svg)](https://aistudio.google.com/)

A minimalist, multi-agent social circle simulation and prediction engine.
*Predicting the butterfly effect of any drama, one agent at a time.*

[English](./README.md) | [中文介绍](./README_ZH.md) | [日本語](./README_JP.md)

</div>

## 📖 What is HaruFishing?

HaruFishing is a lightweight Swarm Intelligence Sandbox inspired by projects like MiroFish. It allows you to input a trigger event and a set of character profiles (personalities, backgrounds, and relationships). The system then spawns autonomous AI agents that role-play these characters, interact in a turn-based "Blackboard" environment, and dynamically generate a force-directed Knowledge Graph of their psychological warfare and actions.

**Key Use Cases:**
- 🎭 **Storyboarding & Writing:** Predict how your characters will react to a plot twist.
- 🏢 **Office Politics Simulation:** Analyze the potential fallout of a workplace event.
- 🍉 **Gossip & Drama Sandbox:** Feed it chat logs, news, or PDFs to see how the drama unfolds.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher.
- A free [Google Gemini API Key](https://aistudio.google.com/).

### Option A: 1-Click Auto Run (Windows)
We provide an automated batch script for a seamless, zero-configuration setup:
1. Double-click `启动_HaruFishing.bat`.
2. Follow the interactive prompts (Y/N) to automatically install Python (if missing) and all required dependencies.
3. The Web UI will automatically launch in your default browser.

### Option B: Manual Run
```bash
# 1. Clone or navigate to the repository
cd D:\HaruFishing

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Set up your API key (or input it directly in the Web UI later)
echo GEMINI_API_KEY=your_api_key_here > .env

# 4. Launch the Web UI
python -m streamlit run ui/web_app.py
```

## 🏗️ Architecture & Core Libraries

HaruFishing is built with a decoupled, three-module architecture to ensure low token consumption, high determinism, and robust error handling.

*   **Module A: Ingestion (`core/ingestion.py`)**
    *   **Document Parsing:** Extracts text from `.txt`, `.pdf`, or `.docx` using `pypdf` and `python-docx`.
    *   **AI Extractor:** Uses Gemini's strict JSON mode to automatically extract core events, characters, and relationships from raw text.
    *   **Prompt Builder:** Converts extracted data into robust System Prompts (`config/prompts.py`).
*   **Module B: Simulation Engine (`core/engine.py`)**
    *   **Blackboard System:** Agents take turns reacting to the evolving situation on a shared context board.
    *   **Incremental Graphing:** Agents output structured JSON at the end of their turns to dynamically build nodes and edges, saving massive amounts of tokens.
    *   **Resilience:** Replaces official SDKs with native HTTP requests and a 60-second timeout to prevent deadlocks, combined with `tenacity` for Exponential Backoff retries against API rate limits (429 errors).
*   **Module C: The Synthesizer (`core/synthesizer.py`)**
    *   **Log Summarization:** A non-participating "Judge" agent (The Observer) reads the interaction logs and predicts 3 near-term outcomes with probabilities.
    *   **Token Optimization:** Auto-truncates excessively long logs before summarization to prevent context window overflows.
    *   **Social Network Analysis (SNA):** Evaluates involved characters with quantitative metrics like Effective Propagation Rate and Social Marketing Score.

## 🌐 Visualization & UI
The frontend is built with **Streamlit** (`ui/web_app.py`). It features:
- **Trilingual Interface:** Instant seamless toggle between English, 中文 (Chinese), and 日本語 (Japanese).
- **Cyber-Geek Aesthetics:** Pure monochrome layout with absolute right angles (0px border-radius), SVG fractal noise topographic background, and "Shippori Mincho" font injection for a top-secret dossier vibe.
- **Real-Time Graph Metrics:** A floating dashboard calculates Network Density, Clustering Coefficient, and Modularity on the fly.
- **Dual-mode Input:** Run the built-in classic "Mercedes" scenario instantly, or upload your own documents for a custom extraction.
- **Dynamic Knowledge Graph:** Integrates **Pyvis** to render a live, force-directed network graph. Watch the nodes (People, Events, Actions) and their relationships grow and repel each other interactively!


## 📸 System Screenshots

<div align="center">
<img src="./assets/ui_cards.png" width="85%" alt="Character Metrics" style="border: 2px solid #555;"/>
<br><em>Character Node Value Metrics & Initial Setup</em><br><br>

<img src="./assets/ui_eval.png" width="85%" alt="Final Evaluation" style="border: 2px solid #555;"/>
<br><em>Final Judgement & Quantitative Social Marketing Score</em><br><br>

<img src="./assets/ui_graph.png" width="85%" alt="Knowledge Graph" style="border: 2px solid #555;"/>
<br><em>Real-Time Force-Directed Knowledge Graph</em><br><br>
</div>

## ⚙️ Dependencies Overview
- `google-generativeai`: Core LLM interactions.
- `pydantic`: Strict data schemas and JSON validation.
- `streamlit`: Web application framework.
- `pyvis`: Interactive network graph rendering.
- `tenacity`: Robust retry logic.
- `pypdf` & `python-docx`: Document parsing capabilities.

---
*Made with 🎀 by Haru & Mangolotis-anon*


<div align="center">
<img src="./assets/harufishing_webfront.png" width="100%" alt="HaruFishing Banner" />
</div>

