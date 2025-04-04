# 跳出框架：实现简易Deep Search Agent

一个基于大语言模型的深度研究助手，能够自动进行多轮深度研究并生成结构化报告。本项目展示了如何在不依赖复杂框架的情况下，实现一个具有反思能力的 AI 研究代理。


## 🌟 功能特点

- 🤖 自动生成研究报告结构
- 🔍 智能搜索相关信息
- 🤔 多轮反思和深入分析
- 📝 生成结构化的 Markdown 格式报告
- 💾 支持自动保存研究报告
- 🔄 支持多个 LLM 提供商（Gemini、智谱 AI）
- 🌐 使用 Tavily 进行网络搜索

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/Congregalis/vanilla-research-agent.git
cd plain_deep_research
```
2. 安装虚拟环境：
```bash
uv venv
source .venv/Scripts/activate
uv pip install -r requirements.txt
```

3. 配置环境变量：
    - 复制 .env.example 为 .env
    - 在 .env 文件中填入你的 API keys：
    ```plaintext
    GEMINI_API_KEY=your_gemini_api_key
    ZHIPUAI_API_KEY=your_zhipuai_api_key
    TAVILY_API_KEY=your_tavily_api_key
    ```

## 🚀 使用方法
### Web 界面（推荐）
1. 运行 Streamlit 应用：
```bash
streamlit run app.py
 ```

2. 在浏览器中访问应用（默认地址： http://localhost:8501 ）
3. 在侧边栏中：
   
   - 输入 LLM Api key
   - 输入研究主题
   - 点击"开始研究"

### 命令行界面
运行命令行版本：

```bash
python agent.py --topic "你的研究主题"
 ```

## 🔧 自定义配置
- NUM_REFLECTIONS ：反思轮次数（默认：2）
- NUM_RESULTS_PER_SEARCH ：每次搜索返回结果数（默认：3）
- CAP_SEARCH_LENGTH ：搜索结果截断长度（默认：20000）

## ⚠️ 注意事项
- 使用前请确保已配置正确的 API keys
- 报告生成可能需要几分钟时间，请耐心等待
- 建议使用虚拟环境运行项目
- 确保网络连接稳定，Gemini 需要魔法环境
