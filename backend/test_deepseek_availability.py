import os
import requests
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_deepseek():
    api_key = os.getenv("CHATAIAPI_KEY")
    base_url = os.getenv("CHATAI_BASE_URL", "https://www.chataiapi.com/v1")
    
    print(f"Testing DeepSeek model with API Key: {api_key[:10]}...")
    print(f"Base URL: {base_url}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Hello, are you DeepSeek? Please reply with 'Yes'."}
        ],
        "max_tokens": 20
    }
    
    print("\nSending request to deepseek-chat...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30  # 30 seconds timeout
        )
        
        duration = time.time() - start_time
        print(f"Request took {duration:.2f} seconds")
        
        if response.status_code == 200:
            print("\n[SUCCESS] DeepSeek model is available!")
            print("Response:", response.json())
        else:
            print(f"\n[FAILURE] Status Code: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"\n[ERROR] Request failed: {str(e)}")

if __name__ == "__main__":
    test_deepseek()
