from tavily import TavilyClient
from config import TAVILY_API_KEY

def tavily_search(query, include_raw_content=True, max_results=5):
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

    return tavily_client.search(query,
                                include_raw_content=include_raw_content,
                                max_results=max_results,
                                timeout=240)['results']

if __name__ == "__main__":
    # 示例使用
    query = "2025 AI Agent 发展趋势"

    # 测试 Tavily 搜索
    print("\n=== Tavily 搜索 ===")
    tavily_results = tavily_search(query)
    print(f"Tavily 搜索结果 for '{query}':\n")
    print(tavily_results)
    for i, result in enumerate(tavily_results, 1):
        print(f"{i}. {result['title']}")
        print(f"   链接: {result['url']}")
        print(f"   内容: {result['content'][:100]}...\n")