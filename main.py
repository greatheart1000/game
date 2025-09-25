# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import requests
import json

# 从环境变量读取 API Key（推荐）
DASHSCOPE_API_KEY ="sk-e9985a0de2164cce8e9b29cbbd6fdad1"

url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DASHSCOPE_API_KEY}"
}
payload = {
    "model": "qwen-image",
    "input": {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": (
                            "原神游戏里面的二次元少女"
                        )
                    }
                ]
            }
        ]
    },
    "parameters": {
        "negative_prompt": "",
        "prompt_extend": True,
        "watermark": False,
        "size": "1328*1328"
    }
}

try:
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    resp.raise_for_status()
except requests.exceptions.RequestException as e:
    print("请求失败：", e)
else:
    # 如果返回 JSON，可直接解析
    try:
        data = resp.json()
    except ValueError:
        print("响应不是 JSON：")
        print(resp.text)
    else:
        print(data)
        # 得到图片的url地址
        url= data['output']['choices'][0]['message']['content'][0]['image']


