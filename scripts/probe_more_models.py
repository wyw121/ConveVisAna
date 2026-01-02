import os, time, requests
API_KEY = os.getenv('API_KEY_OVERRIDE') or os.getenv('API_KEY') or 'sk-yEI0NzjjM24Ec0RUpMyrQQGYN6cvGx27F6XCNYEIxyaigQJP'
BASE = 'https://api.chataiapi.com/v1'
models = [
    'claude-3-5-sonnet-20240620',
    'claude-3-5-sonnet-20241022',
    'claude-3-haiku-20240307',
    'claude-3-opus-20240229',
    'deepseek-chat',
    'deepseek-coder',
    'gpt-3.5-turbo',
    'gpt-4o',
    'gpt-4o-mini',
    'gpt-4-1106-preview',
    'qwen-plus',
    'qwen2.5-72b-instruct',
    'glm-4',
    'gemini-1.5-flash'
]
headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
for m in models:
    payload = {
        'model': m,
        'messages': [{'role': 'user', 'content': 'Hi, please reply with the model name.'}],
        'max_tokens': 8
    }
    print(f"\n=== {m} ===")
    t0 = time.time()
    try:
        resp = requests.post(f"{BASE}/chat/completions", headers=headers, json=payload, timeout=15)
        dt = time.time() - t0
        print(f"status: {resp.status_code}, time: {dt:.2f}s")
        print(resp.text[:400])
    except Exception as e:
        print('error:', e)
