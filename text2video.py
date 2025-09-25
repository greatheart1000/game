#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/9/6 12:17
# @Author  : caijian
# @File    : text2video.py
# @Software: PyCharm
import os
import time
import json
import requests

# 配置项
API_KEY = "sk-e9985a0de2164cce8e9b29cbbd6fdad1"  # 推荐从环境变量读取
# 如果你非要硬编码（不建议），可以直接赋值，例如：
# API_KEY = "sk-xxxx..."
if not API_KEY:
    raise RuntimeError("请先设置环境变量 DASHSCOPE_API_KEY，例如：export DASHSCOPE_API_KEY='sk-xxxx'")

BASE_URL = "https://dashscope.aliyuncs.com"
VIDEO_ENDPOINT = "/api/v1/services/aigc/video-generation/video-synthesis"
TASK_ENDPOINT_TEMPLATE = "/api/v1/tasks/{task_id}"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    # 请求异步任务需要这个头，参照你的 curl 示例
    "X-DashScope-Async": "enable",
}

# 可配置的轮询策略
POLL_INTERVAL_SECONDS = 4      # 每次轮询间隔
MAX_POLL_SECONDS = 300         # 最长等待时间（秒），超时则停止
OUTPUT_DIR = "dashscope_video_task_output"  # 输出目录，脚本会创建
REQUEST_TIMEOUT = 60           # 单次 HTTP 请求超时（秒）

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def post_video_request(prompt_text, model="wan2.2-t2v-plus", size="1920*1080"):
    url = BASE_URL + VIDEO_ENDPOINT
    payload = {
        "model": model,
        "input": {"prompt": prompt_text},
        "parameters": {"size": size}
    }
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def get_task_status(task_id):
    url = BASE_URL + TASK_ENDPOINT_TEMPLATE.format(task_id=task_id)
    resp = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"}, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def save_json(obj, filename):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path

def main():
    ensure_output_dir()

    prompt = "五谷丰登！天赐良机，把握机会"
    print("发送视频生成请求...")
    try:
        post_resp = post_video_request(prompt)
    except requests.exceptions.RequestException as e:
        print("发送请求失败：", e)
        return

    save_json(post_resp, "post_response.json")
    print("POST 响应已保存: post_response.json")
    # 预期返回包含 output.task_id
    task_id = None
    try:
        task_id = post_resp.get("output", {}).get("task_id")
    except Exception:
        task_id = None

    if not task_id:
        print("未在 POST 响应中找到 task_id，完整响应：")
        print(json.dumps(post_resp, ensure_ascii=False, indent=2))
        return

    print("收到 task_id:", task_id)
    save_json({"task_id": task_id}, "task_id.json")

    # 开始轮询任务状态
    start_time = time.time()
    elapsed = 0
    final_resp = None
    print("开始轮询任务状态，直到状态为 SUCCEEDED 或超时...")
    while elapsed < MAX_POLL_SECONDS:
        try:
            status_resp = get_task_status(task_id)
        except requests.exceptions.RequestException as e:
            print("轮询请求失败：", e)
            # 等待后重试
            time.sleep(POLL_INTERVAL_SECONDS)
            elapsed = time.time() - start_time
            continue

        # 保存每次轮询结果（可选：只保存最后一次以节省空间）
        timestamp = int(time.time())
        save_json(status_resp, f"task_status_{timestamp}.json")

        output = status_resp.get("output", {})
        task_status = output.get("task_status") or status_resp.get("task_status")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] task_status = {task_status}")

        if task_status == "SUCCEEDED":
            final_resp = status_resp
            print("任务已完成（SUCCEEDED）")
            break
        elif task_status in ("FAILED", "CANCELED", "ERROR"):
            print("任务失败或被取消，响应：")
            print(json.dumps(status_resp, ensure_ascii=False, indent=2))
            final_resp = status_resp
            break

        time.sleep(POLL_INTERVAL_SECONDS)
        elapsed = time.time() - start_time

    if not final_resp:
        print("任务在限定时间内未完成，停止轮询。最后一次状态：")
        # 保存最后一次状态文件名（上面每次都会保存）
        return

    # 若任务成功，解析 video_url 与 prompts
    out = final_resp.get("output", {})
    video_url = out.get("video_url")
    orig_prompt = out.get("orig_prompt")
    actual_prompt = out.get("actual_prompt")
    submit_time = out.get("submit_time")
    end_time = out.get("end_time")
    usage = final_resp.get("usage", {})

    result = {
        "task_id": task_id,
        "task_status": out.get("task_status"),
        "video_url": video_url,
        "orig_prompt": orig_prompt,
        "actual_prompt": actual_prompt,
        "submit_time": submit_time,
        "end_time": end_time,
        "usage": usage,
        "raw_response": final_resp
    }
    save_path = save_json(result, "task_result.json")
    print("任务结果已保存：", save_path)
    print("video_url:", video_url)
    print("orig_prompt:", orig_prompt)
    print("actual_prompt:", actual_prompt)

    # 可选：自动下载视频（若 video_url 可公开访问）
    if video_url:
        try:
            print("开始下载视频到本地文件 video.mp4 ...")
            dl = requests.get(video_url, stream=True, timeout=REQUEST_TIMEOUT)
            dl.raise_for_status()
            local_video_path = os.path.join(OUTPUT_DIR, f"{task_id}.mp4")
            with open(local_video_path, "wb") as f:
                for chunk in dl.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print("视频已下载到：", local_video_path)
        except requests.exceptions.RequestException as e:
            print("下载视频失败：", e)
            print("你可以在 task_result.json 中找到 video_url，手动下载。")

if __name__ == "__main__":
    main()