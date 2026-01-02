import os
import requests
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_model(model_name):
    api_key = os.getenv("CHATAIAPI_KEY")
    base_url = os.getenv("CHATAI_BASE_URL", "https://www.chataiapi.com/v1")
    
    print(f"\nTesting model: {model_name}")
    print(f"API Key: {api_key[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "Hello, please reply with 'OK'."}
        ],
        "max_tokens": 10
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        duration = time.time() - start_time
        print(f"Request took {duration:.2f} seconds")
        
        if response.status_code == 200:
            print(f"[SUCCESS] {model_name} is available!")
            try:
                print("Response:", response.json()['choices'][0]['message']['content'])
            except:
                print("Response JSON:", response.json())
            return True
        else:
            print(f"[FAILURE] Status Code: {response.status_code}")
            print("Response:", response.text)
            return False
            
    except Exception as e:
        print(f"[ERROR] Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test DeepSeek
    deepseek_result = test_model("deepseek-chat")
    
    # Test Claude (Current Default)
    claude_result = test_model("claude-3-5-sonnet-20240620")
    
    print("\n" + "="*30)
    print("Summary:")
    print(f"DeepSeek: {'✅ Available' if deepseek_result else '❌ Unavailable'}")
    print(f"Claude:   {'✅ Available' if claude_result else '❌ Unavailable'}")
    print("="*30)
