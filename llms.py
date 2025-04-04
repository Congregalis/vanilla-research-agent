from abc import ABC, abstractmethod
from google import genai
from zhipuai import ZhipuAI

class BaseLLM(ABC):
    @abstractmethod
    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        pass

class GeminiLLM(BaseLLM):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.default_model_type = 'gemini-2.0-flash'
        
    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        combined_prompt = f"{system_prompt}\n{user_prompt}"
        
        response = self.client.models.generate_content(
            model=self.default_model_type,
            contents=combined_prompt
        )
        return response.text if response.text is not None else ""

class ZhipuAILLM(BaseLLM):
    def __init__(self, api_key: str):
        self.client = ZhipuAI(api_key=api_key) 
        self.default_model_type = 'charglm-4'
        
    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.default_model_type,
            messages=messages,
        )
        
        return response.choices[0].message.content if response.choices[0].message.content is not None else ""

# 使用示例
def main():
    # Gemini示例
    gemini_api_key = "your api key"
    gemini_llm = GeminiLLM(gemini_api_key)
    
    # 智谱AI示例
    zhipuai_api_key = "your api key"
    zhipuai_llm = ZhipuAILLM(zhipuai_api_key)
    
    # 测试提示
    system_prompt = "你是一个有帮助的AI助手。"
    user_prompt = "请简要介绍一下Python。"
    
    try:
        # 测试 Gemini
        print("===== Test Gemini =====\n")
        gemini_response = gemini_llm.invoke(system_prompt, user_prompt)
        print("Gemini 响应:", gemini_response)
        
        # 测试 智谱AI
        print("===== Test Zhipu =====\n")
        zhipuai_response = zhipuai_llm.invoke(system_prompt, user_prompt)
        print("智谱AI 响应:", zhipuai_response)
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()