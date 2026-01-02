import requests, time, os
API_KEY = os.getenv('API_KEY_OVERRIDE') or 'sk-yEI0NzjjM24Ec0RUpMyrQQGYN6cvGx27F6XCNYEIxyaigQJP'
BASE = 'https://api.chataiapi.com/v1'
models = [
    'claude-3-5-sonnet-20240620',
    'deepseek-chat',
    'deepseek-coder',
    'gpt-3.5-turbo'
]
headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
for m in models:
    payload = {'model': m, 'messages': [{'role': 'user', 'content': 'Hi, reply with model name.'}], 'max_tokens': 8}
    print(f"\n=== {m} ===")
    t0 = time.time()
    try:
        resp = requests.post(f"{BASE}/chat/completions", headers=headers, json=payload, timeout=15)
        dt = time.time() - t0
        print(f"status: {resp.status_code}, time: {dt:.2f}s")
        print(resp.text[:400])
    except Exception as e:
        print('error:', e)
