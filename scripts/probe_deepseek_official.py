import os, requests, time

def probe():
    key = os.getenv('API_KEY_OVERRIDE') or os.getenv('API_KEY')
    if not key:
        print('No API key found in env')
        return
    base = 'https://api.deepseek.com/v1'
    models = ['deepseek-chat', 'deepseek-reasoner']
    headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    for m in models:
        payload = {'model': m, 'messages': [{'role': 'user', 'content': 'Hi, reply with model name.'}], 'max_tokens': 16}
        print(f"\n=== {m} ===")
        t0 = time.time()
        try:
            r = requests.post(f"{base}/chat/completions", headers=headers, json=payload, timeout=15)
            dt = time.time() - t0
            print('status:', r.status_code, 'time:', f'{dt:.2f}s')
            print(r.text[:400])
        except Exception as e:
            print('error:', e)

if __name__ == '__main__':
    probe()
