#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/9/7 17:28
# @Author  : caijian
# @File    : 222.py
# @Software: PyCharm
import os
import time
# 通过 pip install 'volcengine-python-sdk[ark]' 安装方舟SDK
from volcenginesdkarkruntime import Ark

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key = "f62bafd2-1269-4169-b072-7994b36541a7",
)

if __name__ == "__main__":
    print("----- create request -----")
    create_result = client.content_generation.tasks.create(
        # 替换 <Model> 为模型的Model ID
        model = "doubao-seaweed-241128",
        content = [
            {
                # 文本提示词
                "type": "text",
                "text": "关羽温酒斩华雄 --rs 720p --rt 16:9 --dur 5 --fps 24 --wm true --seed 11 --cf false"
            },        ])
    print(create_result)

    # 轮询查询部分
    print("----- pooling task status -----")
    task_id = create_result.id
    while True:
        get_result = client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        if status == "succeeded":
            print("----- task succeeded -----")
            print(get_result)
            break
        elif status == "failed":
            print("----- task failed -----")
            print(f"Error: {get_result.error}")
            break
        else:
            print(f"Current status: {status}, Retrying after 10 seconds...")
            time.sleep(10)
