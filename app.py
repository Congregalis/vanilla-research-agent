import streamlit as st
import json
from datetime import datetime
import os
from nodes import (
    ReportStructureNode, 
    FirstSearchNode, 
    FirstSummaryNode, 
    ReflectionNode, 
    ReflectionSummaryNode, 
    ReportFormattingNode
)
from state import State
from tools import tavily_search
from utils import update_state_with_search_results
from llms import GeminiLLM, ZhipuAILLM
from config import (
    GEMINI_API_KEY, 
    NUM_REFLECTIONS, 
    NUM_RESULTS_PER_SEARCH, 
    CAP_SEARCH_LENGTH
)

# 页面配置
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔍",
    layout="wide"
)

# 初始化会话状态
if 'state' not in st.session_state:
    st.session_state.state = State()
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'final_report' not in st.session_state:
    st.session_state.final_report = None

# 常量设置
# NUM_REFLECTIONS = 2
# NUM_RESULTS_PER_SEARCH = 3
# CAP_SEARCH_LENGTH = 20000

# 主标题
st.title("🤖 AI 深度研究助手")

# 侧边栏配置
with st.sidebar:
    st.header("配置")
    api_key = st.text_input("Gemini API Key", value=GEMINI_API_KEY, type="password")
    topic = st.text_input("研究主题", value="2025年AI趋势是什么？")
    
    if st.button("开始研究", type="primary"):
        st.session_state.current_step = 1
        st.session_state.state = State()
        
        # 初始化 LLM
        llm_client = GeminiLLM(api_key)
        
        # 创建报告结构
        with st.spinner("正在生成报告结构..."):
            report_structure_node = ReportStructureNode(llm_client, topic)
            _ = report_structure_node.mutate_state(st.session_state.state)
            st.success("报告结构已生成！")

# 主要内容区域
if st.session_state.current_step >= 1:
    # 先展示完整的报告结构
    st.header("📋 完整报告结构")
    with st.expander("查看完整报告结构", expanded=True):
        for idx, paragraph in enumerate(st.session_state.state.paragraphs, 1):
            st.markdown(f"""
            ### 第 {idx} 部分：{paragraph.title}
            <div style="font-size: 1rem; margin-left: 1rem;">
            {paragraph.content}
            </div>
            ---
            """, unsafe_allow_html=True)
    
    # 详细研究过程
    st.header("📑 详细研究过程")
    for idx, paragraph in enumerate(st.session_state.state.paragraphs, 1):
        st.subheader(f"段落 {idx}: {paragraph.title}")
        
        # 为每个段落创建一个展开区域
        with st.expander(f"查看段落 {idx} 的研究过程", expanded=True):
            llm_client = GeminiLLM(api_key)
            
            # 初始化节点
            first_search_node = FirstSearchNode(llm_client)
            first_summary_node = FirstSummaryNode(llm_client)
            reflection_node = ReflectionNode(llm_client)
            reflection_summary_node = ReflectionSummaryNode(llm_client)
            
            # 第一次搜索
            st.write("🔍 **初始搜索**")
            message = json.dumps({
                "title": paragraph.title,
                "content": paragraph.content
            })
            
            with st.spinner("正在进行初始搜索..."):
                output = first_search_node.run(message)
                st.write("搜索查询:", output.get("search_query"))
                st.write("推理过程:", output.get("reasoning"))
                
                search_results = tavily_search(output.get("search_query"), max_results=NUM_RESULTS_PER_SEARCH)
                
                # 使用 columns 替代嵌套的 expander
                st.write("**搜索结果:**")
                for i, result in enumerate(search_results, 1):
                    with st.container():
                        st.markdown(f"""
                        <div style="font-size: 0.9rem; margin-left: 1rem;">
                        <strong>结果 {i}:</strong><br/>
                        📌 <strong>标题:</strong> {result['title']}<br/>
                        🔗 <strong>链接:</strong> {result['url']}<br/>
                        📝 <strong>摘要:</strong> {result['content'][:200]}...
                        </div>
                        ---
                        """, unsafe_allow_html=True)
                
                _ = update_state_with_search_results(search_results, idx-1, st.session_state.state)
            
            # 初始总结
            st.write("📝 **初始总结**")
            message = {
                "title": paragraph.title,
                "content": paragraph.content,
                "search_query": output.get("search_query"),
                "search_results": [result["content"][0:CAP_SEARCH_LENGTH] for result in search_results if result["content"]]
            }
            
            with st.spinner("正在生成初始总结..."):
                _ = first_summary_node.mutate_state(message=json.dumps(message, ensure_ascii=False), idx_paragraph=idx-1, state=st.session_state.state)
                summary = st.session_state.state.paragraphs[idx-1].research.latest_summary
                if isinstance(summary, str):
                    st.markdown(f"""
                    <div style="font-size: 0.95rem; margin-left: 1rem; background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;">
                    {summary}
                    </div>
                    """, unsafe_allow_html=True)
                elif isinstance(summary, dict) and "paragraph_latest_state" in summary:
                    st.markdown(f"""
                    <div style="font-size: 0.95rem; margin-left: 1rem; background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;">
                    {summary["paragraph_latest_state"]}
                    </div>
                    """, unsafe_allow_html=True)
            st.write(st.session_state.state.paragraphs[idx-1].research.latest_summary)
            
            # 反思阶段
            for i in range(NUM_REFLECTIONS):
                st.write(f"🤔 **反思 {i+1}**")
                
                message = {
                    "paragraph_latest_state": st.session_state.state.paragraphs[idx-1].research.latest_summary,
                    "title": paragraph.title,
                    "content": paragraph.content
                }
                
                with st.spinner(f"正在进行第 {i+1} 次反思..."):
                    output = reflection_node.run(message=json.dumps(message))
                    st.write(f"反思搜索查询:", output.get("search_query"))
                    st.write(f"反思推理:", output.get("reasoning"))
                    
                    search_results = tavily_search(output.get("search_query"))
                    st.write(f"**反思 {i+1} 的搜索结果:**")
                    for j, result in enumerate(search_results, 1):
                        with st.container():
                            st.markdown(f"""
                            <div style="font-size: 0.9rem; margin-left: 1rem;">
                            <strong>结果 {j}:</strong><br/>
                            📌 <strong>标题:</strong> {result['title']}<br/>
                            🔗 <strong>链接:</strong> {result['url']}<br/>
                            📝 <strong>摘要:</strong> {result['content'][:200]}...
                            </div>
                            ---
                            """, unsafe_allow_html=True)
                    
                    _ = update_state_with_search_results(search_results, idx-1, st.session_state.state)
                    
                    message = {
                        "title": paragraph.title,
                        "content": paragraph.content,
                        "search_query": output.get("search_query"),
                        "search_results": [result["content"][0:20000] for result in search_results if result["content"]],
                        "paragraph_latest_state": st.session_state.state.paragraphs[idx-1].research.latest_summary
                    }
                    
                    _ = reflection_summary_node.mutate_state(message=json.dumps(message, ensure_ascii=False), idx_paragraph=idx-1, state=st.session_state.state)
                    st.write("反思后的总结:")
                    st.write(st.session_state.state.paragraphs[idx-1].research.latest_summary)

    # 生成最终报告
    st.header("📊 最终报告")
    report_formatting_node = ReportFormattingNode(llm_client)
    report_data = [{"title": paragraph.title, "paragraph_latest_state": paragraph.research.latest_summary} 
                  for paragraph in st.session_state.state.paragraphs]
    
    with st.spinner("正在生成最终报告..."):
        final_report = report_formatting_node.run(json.dumps(report_data))
        st.session_state.final_report = final_report
        st.markdown(final_report)
        
        # 保存报告
        os.makedirs("reports", exist_ok=True)
        report_path = f"reports/report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(final_report)
        
        st.success(f"报告已保存到: {report_path}")