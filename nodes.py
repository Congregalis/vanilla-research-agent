import json
from json.decoder import JSONDecodeError
from prompts import SYSTEM_PROMPT_REPORT_STRUCTURE, SYSTEM_PROMPT_FIRST_SEARCH, SYSTEM_PROMPT_FIRST_SUMMARY, SYSTEM_PROMPT_REFLECTION, \
    SYSTEM_PROMPT_REPORT_FORMATTING, SYSTEM_PROMPT_REFLECTION_SUMMARY
from state import State, Paragraph, Research, Search
from utils import clean_json_tags, remove_reasoning_from_output, clean_markdown_tags, extract_clean_response
from llms import BaseLLM


import json
from json.decoder import JSONDecodeError
from prompts import (SYSTEM_PROMPT_REPORT_STRUCTURE, SYSTEM_PROMPT_FIRST_SEARCH, 
                    SYSTEM_PROMPT_FIRST_SUMMARY, SYSTEM_PROMPT_REFLECTION, 
                    SYSTEM_PROMPT_REFLECTION_SUMMARY, SYSTEM_PROMPT_REPORT_FORMATTING)
from state import State, Paragraph, Research, Search
from utils import clean_json_tags, remove_reasoning_from_output, clean_markdown_tags, extract_clean_response
from llms import BaseLLM

class ReportStructureNode:
    """生成报告结构的节点"""
    def __init__(self, llm_client: BaseLLM, query: str):
        self.llm_client = llm_client
        self.query = query

    def run(self) -> str:
        """调用LLM生成报告结构"""
        response = self.llm_client.invoke(SYSTEM_PROMPT_REPORT_STRUCTURE, self.query)
        return response

    def mutate_state(self, state: State) -> State:
        """将报告结构写入状态"""
        report_structure = self.run()
        report_structure = remove_reasoning_from_output(report_structure)
        report_structure = clean_json_tags(report_structure)

        report_structure = json.loads(report_structure)
        for paragraph in report_structure:
            state.paragraphs.append(Paragraph(title=paragraph["title"], content=paragraph["content"]))
        return state    

class FirstSearchNode:
    """为段落生成首次搜索查询的节点"""
    def __init__(self, llm_client: BaseLLM):
        self.llm_client = llm_client

    def run(self, message: str) -> dict:
        """调用LLM生成搜索查询和理由"""
        response = self.llm_client.invoke(SYSTEM_PROMPT_FIRST_SEARCH, message)
        response = remove_reasoning_from_output(response)
        response = clean_json_tags(response)
        response_dict = extract_clean_response(response)  # 提取干净的JSON字典
        return response_dict

class FirstSummaryNode:
    """根据搜索结果生成段落首次总结的节点"""
    def __init__(self, llm_client: BaseLLM):
        self.llm_client = llm_client

    def run(self, message: str) -> str:
        """调用LLM生成段落总结"""
        response = self.llm_client.invoke(SYSTEM_PROMPT_FIRST_SUMMARY, message)
        return response

    def mutate_state(self, message: str, idx_paragraph: int, state: State) -> State:
        """更新段落的最新总结到状态"""
        summary = self.run(message)
        summary = remove_reasoning_from_output(summary)
        summary = clean_json_tags(summary)
        
        try:
            summary = json.loads(summary)
        except JSONDecodeError:
            summary = {"paragraph_latest_state": summary}  # 容错处理非JSON输出

        state.paragraphs[idx_paragraph].research.latest_summary = summary["paragraph_latest_state"]
        return state

class ReflectionNode:
    """反思段落并生成新搜索查询的节点"""
    def __init__(self, llm_client: BaseLLM):
        self.llm_client = llm_client

    def run(self, message: str) -> dict:
        """调用LLM反思并生成搜索查询"""
        response = self.llm_client.invoke(SYSTEM_PROMPT_REFLECTION, message)
        response = remove_reasoning_from_output(response)
        response = clean_json_tags(response)
        response_dict = extract_clean_response(response)
        return response_dict

class ReflectionSummaryNode:
    """根据反思搜索结果更新段落总结的节点"""
    def __init__(self, llm_client: BaseLLM):
        self.llm_client = llm_client

    def run(self, message: str) -> str:
        """调用LLM更新段落内容"""
        response = self.llm_client.invoke(SYSTEM_PROMPT_REFLECTION_SUMMARY, message)
        return response

    def mutate_state(self, message: str, idx_paragraph: int, state: State) -> State:
        """将更新后的总结写入状态"""
        summary = self.run(message)
        summary = remove_reasoning_from_output(summary)
        summary = clean_json_tags(summary)

        try:
            summary = json.loads(summary)
        except JSONDecodeError:
            summary = {"updated_paragraph_latest_state": summary}  # 容错处理

        state.paragraphs[idx_paragraph].research.latest_summary = summary["updated_paragraph_latest_state"]
        return state

class ReportFormattingNode:
    """格式化最终报告的节点"""
    def __init__(self, llm_client: BaseLLM):
        self.llm_client = llm_client

    def run(self, message: str) -> str:
        """调用LLM生成Markdown格式报告"""
        response = self.llm_client.invoke(SYSTEM_PROMPT_REPORT_FORMATTING, message)
        response = remove_reasoning_from_output(response)
        response = clean_markdown_tags(response)
        return response


def main():
    from llms import GeminiLLM
    from state import State

    # 初始化 LLM 客户端
    api_key = "your api key"
    llm_client = GeminiLLM(api_key)
    
    # 初始化状态
    state = State()
    
    try:
        print("===== 测试 ReportStructureNode =====")
        query = "介绍一下人工智能的发展历史"
        report_structure_node = ReportStructureNode(llm_client, query)
        state = report_structure_node.mutate_state(state)
        print("报告结构已生成，段落数量:", len(state.paragraphs))
        for i, para in enumerate(state.paragraphs):
            print(f"\n段落 {i+1}:")
            print(f"标题: {para.title}")
            print(f"内容: {para.content}")

        # 为第一个段落进行搜索和总结测试
        if state.paragraphs:
            print("\n===== 测试 FirstSearchNode =====")
            first_search_node = FirstSearchNode(llm_client)
            search_message = {
                "title": state.paragraphs[0].title,
                "content": state.paragraphs[0].content
            }
            search_result = first_search_node.run(json.dumps(search_message))
            print("搜索查询:", search_result.get("search_query"))
            print("推理过程:", search_result.get("reasoning"))

            print("\n===== 测试 FirstSummaryNode =====")
            first_summary_node = FirstSummaryNode(llm_client)
            summary_message = {
                "title": state.paragraphs[0].title,
                "content": state.paragraphs[0].content,
                "search_query": "test_search_query",
                "search_results": ["\"人工智能之父\" 艾伦·图灵。 1、 人工智能的诞生（20世纪40～50年代） 1950年：图灵测试 1950年，著名的图灵测试诞生，按照、\"人工智能之父\"艾伦·图灵的定义：如果一台机器能够与人类展开对话（通过电传设备）而不能被辨别出其机器身份，那么称这台机器具有智能。", "1950年：图灵发表《计算机器与智能》，提出\"图灵测试\"，定义机器智能的评估标准。 1956年 ： 达特茅斯会议 召开，约翰·麦卡锡、 马文·明斯基 等学者首次提出\"人工智能\"术语，标志着AI成为独立学科。"]
            }
            state = first_summary_node.mutate_state(json.dumps(summary_message, ensure_ascii=False), 0, state)
            print("第一段总结:", state.paragraphs[0].research.latest_summary)

            print("\n===== 测试 ReflectionNode =====")
            reflection_node = ReflectionNode(llm_client)
            reflection_message = {
                "title": state.paragraphs[0].title,
                "content": state.paragraphs[0].content,
                "paragraph_latest_state": state.paragraphs[0].research.latest_summary
            }
            reflection_result = reflection_node.run(json.dumps(reflection_message))
            print("反思查询:", reflection_result.get("search_query"))
            print("反思推理:", reflection_result.get("reasoning"))

            print("\n===== 测试 ReflectionSummaryNode =====")
            reflection_summary_node = ReflectionSummaryNode(llm_client)
            reflection_summary_message = {
                "title": state.paragraphs[0].title,
                "content": state.paragraphs[0].content,
                "search_query": reflection_result.get("search_query"),
                "search_results": ["这是一个模拟的反思搜索结果"],
                "paragraph_latest_state": state.paragraphs[0].research.latest_summary
            }
            state = reflection_summary_node.mutate_state(json.dumps(reflection_summary_message), 0, state)
            print("反思后的总结:", state.paragraphs[0].research.latest_summary)

        print("\n===== 测试 ReportFormattingNode =====")
        formatting_node = ReportFormattingNode(llm_client)
        formatting_message = [
            {
                "title": para.title,
                "paragraph_latest_state": para.research.latest_summary or para.content
            }
            for para in state.paragraphs
        ]
        final_report = formatting_node.run(json.dumps(formatting_message))
        print("最终报告:\n", final_report)

    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()