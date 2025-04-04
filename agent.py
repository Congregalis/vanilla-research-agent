import json
import argparse
import os
from datetime import datetime

from nodes import (ReportStructureNode, FirstSearchNode, FirstSummaryNode, 
                  ReflectionNode, ReflectionSummaryNode, ReportFormattingNode)
from state import State
from tools import tavily_search
from utils import update_state_with_search_results
from llms import ZhipuAILLM
from config import (
    ZHIPUAI_API_KEY, 
    NUM_REFLECTIONS, 
    NUM_RESULTS_PER_SEARCH, 
    CAP_SEARCH_LENGTH
)

# 全局配置
STATE = State()
QUERY = "2025年黄金"
# NUM_REFLECTIONS = 2  # 反思次数
# NUM_RESULTS_PER_SEARCH = 3  # 每次搜索结果数
# CAP_SEARCH_LENGTH = 20000  # 搜索内容截断长度

def main(topic: str = QUERY):
    # 初始化LLM客户端
    # llm_client = GeminiLLM(GEMINI_API_KEY)
    llm_client = ZhipuAILLM(ZHIPUAI_API_KEY)

    # 创建所有节点实例
    report_structure_node = ReportStructureNode(llm_client, topic)
    first_search_node = FirstSearchNode(llm_client)
    first_summary_node = FirstSummaryNode(llm_client)
    reflection_node = ReflectionNode(llm_client)
    reflection_summary_node = ReflectionSummaryNode(llm_client)
    report_formatting_node = ReportFormattingNode(llm_client)

    # Step 1: 生成报告结构并更新状态
    _ = report_structure_node.mutate_state(STATE)
    print(f"总段落数: {len(STATE.paragraphs)}")
    for idx, paragraph in enumerate(STATE.paragraphs, 1):
        print(f"\n段落 {idx}: {paragraph.title}")

    # Step 2: 遍历每个段落，执行搜索和反思
    for j in range(len(STATE.paragraphs)):
        print(f"\n\n============== 段落 {j+1} ==============\n")
        print(f"============== {STATE.paragraphs[j].title} ==============\n")

        # 初始搜索
        message = json.dumps({"title": STATE.paragraphs[j].title, "content": STATE.paragraphs[j].content}, ensure_ascii=False)
        output = first_search_node.run(message)
        print("\n[初始搜索] 查询:", output.get("search_query"))
        print("[初始搜索] 推理:", output.get("reasoning"))
        
        search_results = tavily_search(output.get("search_query"), max_results=NUM_RESULTS_PER_SEARCH)
        print("\n[搜索结果]:")
        for idx, result in enumerate(search_results, 1):
            print(f"\n结果 {idx}:")
            print(f"标题: {result['title']}")
            print(f"链接: {result['url']}")
            print(f"摘要: {result['content'][:200]}...")
        
        _ = update_state_with_search_results(search_results, j, STATE)
        
        # 初始总结
        message = {
            "title": STATE.paragraphs[j].title,
            "content": STATE.paragraphs[j].content,
            "search_query": output.get("search_query"),
            "search_results": [result["content"][:CAP_SEARCH_LENGTH] for result in search_results if result["content"]]
        }
        _ = first_summary_node.mutate_state(json.dumps(message, ensure_ascii=False), j, STATE)
        print("\n[初始总结]:")
        print(STATE.paragraphs[j].research.latest_summary)
        
        # 反思循环
        for i in range(NUM_REFLECTIONS):
            print(f"\n[反思 {i+1}] 开始...")
            message = {
                "paragraph_latest_state": STATE.paragraphs[j].research.latest_summary,
                "title": STATE.paragraphs[j].title,
                "content": STATE.paragraphs[j].content
            }
            output = reflection_node.run(json.dumps(message, ensure_ascii=False))
            print(f"\n[反思 {i+1}] 查询:", output.get("search_query"))
            print(f"[反思 {i+1}] 推理:", output.get("reasoning"))
            
            search_results = tavily_search(output.get("search_query"), max_results=NUM_RESULTS_PER_SEARCH)
            print(f"\n[反思 {i+1}] 搜索结果:")
            for idx, result in enumerate(search_results, 1):
                print(f"\n结果 {idx}:")
                print(f"标题: {result['title']}")
                print(f"链接: {result['url']}")
                print(f"摘要: {result['content'][:200]}...")
            
            _ = update_state_with_search_results(search_results, j, STATE)
            
            message = {
                "title": STATE.paragraphs[j].title,
                "content": STATE.paragraphs[j].content,
                "search_query": output.get("search_query"),
                "search_results": [result["content"][:CAP_SEARCH_LENGTH] for result in search_results if result["content"]],
                "paragraph_latest_state": STATE.paragraphs[j].research.latest_summary
            }
            _ = reflection_summary_node.mutate_state(json.dumps(message, ensure_ascii=False), j, STATE)
            print(f"\n[反思 {i+1}] 更新总结:")
            print(STATE.paragraphs[j].research.latest_summary)

    # Step 3: 生成最终报告
    print("\n=============== 最终报告生成 ===============\n")
    report_data = [{"title": p.title, "paragraph_latest_state": p.research.latest_summary} for p in STATE.paragraphs]
    final_report = report_formatting_node.run(json.dumps(report_data, ensure_ascii=False))
    
    print("\n=============== 最终报告 ===============\n")
    print(final_report)

    # 保存到文件
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_report)
    print(f"\n报告已保存至: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deep Search Agent")
    parser.add_argument("--topic", type=str, default=QUERY, help="研究主题")
    args = parser.parse_args()
    main(args.topic)