#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/9/7 17:32
# @Author  : caijian
# @File    : vidio_seaweed.py
# @Software: PyCharm
import os
from volcenginesdkarkruntime import Ark

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key

client = Ark(
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("ARK_API_KEY"),
)

print("----- create i2v request -----")
# 创建 图生视频 任务
create_result = client.content_generation.tasks.create(
    model="doubao-seedance-1-0-lite-i2v-250428",
    content=[
        {
            # 文本提示词与参数组合
            "type": "text",
            "text": "女孩抱着狐狸，女孩睁开眼，温柔地看向镜头，狐狸友善地抱着，镜头缓缓拉出，女孩的头发被风吹动  --resolution 720p  --dur 5 --camerafixed false"
        },
        {
            # 图片URL
            "type": "image_url",
            "image_url": {
                "url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/i2v_foxrgirl.png" #请上传可以访问的图片URL
            }
        }
    ]
)
print(create_result)


print("----- get request -----")
# 获取任务详情
get_result = client.content_generation.tasks.get(task_id=create_result.id)
print(get_result)


print("----- list request -----")
# 列出符合特定条件的任务
list_result = client.content_generation.tasks.list(
    page_num=1,
    page_size=10,
    status="queued",  # 按状态筛选, e.g succeeded, failed, running, cancelled
    # model="doubao-seedance-1-0-lite-i2v-250428", # 按 ep 筛选
    # task_ids=["test-id-1", "test-id-2"] # 按 task_id 筛选
)
print(list_result)


print("----- delete request -----")
# 通过任务 id 删除任务
try:
    client.content_generation.tasks.delete(task_id=create_result.id)
    print(create_result.id)
except Exception as e:
    print(f"failed to delete task: {e}")