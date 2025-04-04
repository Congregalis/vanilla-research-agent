import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Custom Settings
NUM_REFLECTIONS = int(os.getenv("NUM_REFLECTIONS", 2))
NUM_RESULTS_PER_SEARCH = int(os.getenv("NUM_RESULTS_PER_SEARCH", 3))
CAP_SEARCH_LENGTH = int(os.getenv("CAP_SEARCH_LENGTH", 20000))

# 检查必要的环境变量
def check_api_keys():
    missing_keys = []
    if not GEMINI_API_KEY:
        missing_keys.append("GEMINI_API_KEY")
    if not ZHIPUAI_API_KEY:
        missing_keys.append("ZHIPUAI_API_KEY")
    if not TAVILY_API_KEY:
        missing_keys.append("TAVILY_API_KEY")
    
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")