"""路径与运行配置。

CineSolo 的项目数据统一存放在数据盘（服务器上是 /root/autodl-tmp/CineSolo），
不占用系统盘。本地开发机上没有这个路径，可用 CINESOLO_DATA_ROOT 环境变量覆盖，
方便在本地跑测试/调试。
"""

from __future__ import annotations

import os
from pathlib import Path

# 服务器上的默认数据盘挂载点（见 docs/REQUIREMENTS.md 3.1 目录规范）
DEFAULT_DATA_ROOT = Path("/root/autodl-tmp/CineSolo")


def get_data_root() -> Path:
    """返回CineSolo数据根目录，优先读取 CINESOLO_DATA_ROOT 环境变量。"""
    override = os.environ.get("CINESOLO_DATA_ROOT")
    return Path(override) if override else DEFAULT_DATA_ROOT


def get_projects_root() -> Path:
    return get_data_root() / "projects"


def get_project_dir(project: str) -> Path:
    return get_projects_root() / project


def get_episode_dir(project: str, episode: str) -> Path:
    return get_project_dir(project) / episode


def get_shot_dir(project: str, episode: str, shot_id: str) -> Path:
    return get_episode_dir(project, episode) / shot_id


def get_comfyui_base_url() -> str:
    """ComfyUI HTTP API地址。默认只监听127.0.0.1:6006，CineSolo需要在服务器本机跑，
    或用 COMFYUI_BASE_URL 环境变量指向AutoDL的公网代理地址。见 docs/REQUIREMENTS.md。
    """
    return os.environ.get("COMFYUI_BASE_URL", "http://127.0.0.1:6006")
