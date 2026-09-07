"""ComfyUI HTTP API的最小客户端。

只封装REQ-001用得到的三个接口：提交任务(POST /prompt)、查询结果(GET /history/<id>)、
下载生成的图片(GET /view)。协议细节见 docs/REQUIREMENTS.md 5. 技术选型。
"""

from __future__ import annotations

import time
import uuid
from typing import Any

import requests


class ComfyUIError(RuntimeError):
    pass


class ComfyUIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:6006", client_id: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id or str(uuid.uuid4())

    def submit_prompt(self, workflow: dict[str, Any]) -> str:
        """提交一个API格式的workflow，返回prompt_id。"""
        resp = requests.post(
            f"{self.base_url}/prompt",
            json={"prompt": workflow, "client_id": self.client_id},
            timeout=30,
        )
        if resp.status_code != 200:
            raise ComfyUIError(f"提交任务失败 ({resp.status_code}): {resp.text[:500]}")
        data = resp.json()
        if "prompt_id" not in data:
            raise ComfyUIError(f"提交任务返回异常: {data}")
        return data["prompt_id"]

    def wait_for_result(self, prompt_id: str, timeout: float = 300, poll_interval: float = 2) -> dict[str, Any]:
        """轮询 /history/<prompt_id> 直到任务完成，返回该次任务的history条目。"""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            resp = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if prompt_id in data:
                    return data[prompt_id]
            time.sleep(poll_interval)
        raise ComfyUIError(f"等待任务 {prompt_id} 超时 (>{timeout}s)")

    def extract_images(self, history_entry: dict[str, Any]) -> list[dict[str, str]]:
        """从history条目里提取所有输出图片的 {filename, subfolder, type}。"""
        images = []
        outputs = history_entry.get("outputs", {})
        for node_output in outputs.values():
            for img in node_output.get("images", []):
                images.append(img)
        return images

    def fetch_image(self, filename: str, subfolder: str = "", type_: str = "output") -> bytes:
        resp = requests.get(
            f"{self.base_url}/view",
            params={"filename": filename, "subfolder": subfolder, "type": type_},
            timeout=30,
        )
        if resp.status_code != 200:
            raise ComfyUIError(f"下载图片失败 ({resp.status_code}): {filename}")
        return resp.content
