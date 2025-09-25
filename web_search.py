#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/9/6 17:43
# @Author  : caijian
# @File    : web_search.py
# @Software: PyCharm
import dashscope

messages = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': '今天白银有什么消息呢'}
    ]
response = dashscope.Generation.call(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key= "sk-e9985a0de2164cce8e9b29cbbd6fdad1",
    model="qwen-plus", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=messages,
    enable_search=True,
    result_format='message'
    )
content = response['output']['choices'][0]['message']['content']
print(content)