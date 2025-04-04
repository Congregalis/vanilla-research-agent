from dataclasses import dataclass, field
from typing import List

@dataclass
class Search:
    """单个搜索结果的状态"""
    url: str = ""          # 搜索结果的链接
    content: str = ""      # 搜索返回的内容

@dataclass
class Research:
    """段落研究过程的状态"""
    search_history: List[Search] = field(default_factory=list)  # 搜索记录列表
    latest_summary: str = ""                                    # 当前段落的最新总结
    reflection_iteration: int = 0                               # 反思迭代次数

@dataclass
class Paragraph:
    """报告中单个段落的状态"""
    title: str = ""                # 段落标题
    content: str = ""              # 段落的预期内容（初始规划）
    research: Research = field(default_factory=Research)  # 研究进度

@dataclass
class State:
    """整个报告的状态"""
    report_title: str = ""                    # 报告标题
    paragraphs: List[Paragraph] = field(default_factory=list)  # 段落列表


if __name__ == "__main__":
    # 示例：初始化状态
    state = State(report_title="2025 AI Agent 发展趋势")
    state.paragraphs.append(Paragraph(title="多模态AI", content="介绍多模态AI的发展"))
    state.paragraphs[0].research.search_history.append(Search(url="example.com", content="教育领域增长30%"))
    state.paragraphs[0].research.latest_summary = "多模态AI在教育领域有显著应用。"
    state.paragraphs[0].research.reflection_iteration = 1

    print(state)