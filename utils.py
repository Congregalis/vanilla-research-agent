from state import Search
import json
import re

from json.decoder import JSONDecodeError

def remove_reasoning_from_output(output):
    return output.split("</think>")[-1].strip()

def clean_json_tags(text):
    return text.replace("```json\n", "").replace("\n```", "")

def clean_markdown_tags(text):
    return text.replace("```markdown\n", "").replace("\n```", "")

def extract_clean_response(response: str) -> dict:
    """处理 LLM 返回的响应，提取搜索信息"""
    try:
        # 尝试直接解析 JSON
        return json.loads(response)
    except JSONDecodeError:
        # 使用正则表达式提取搜索查询和推理
        search_query = ""
        reasoning = ""
        
        # 尝试匹配 search_query
        query_match = re.search(r'"search_query":\s*"([^"]*)"', response)
        if query_match:
            search_query = query_match.group(1)
        else:
            # 备用方案：提取引号之间的内容作为查询
            query_match = re.search(r'"([^"]*)"', response)
            if query_match:
                search_query = query_match.group(1)
            else:
                # 最后的备用方案：使用整个响应
                search_query = response.strip()

        # 尝试匹配 reasoning
        reason_match = re.search(r'"reasoning":\s*"([^"]*)"', response)
        if reason_match:
            reasoning = reason_match.group(1)
            
        return {
            "search_query": search_query,
            "reasoning": reasoning or "从响应中提取的查询"
        }

def update_state_with_search_results(search_results, idx_paragraph, state):
    
    for search_result in search_results:
        search = Search(url=search_result["url"], content=search_result["content"])
        state.paragraphs[idx_paragraph].research.search_history.append(search)

    return state