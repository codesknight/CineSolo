"""分镜脚本（storyboard.yaml）的数据结构、加载与校验。

格式定义见 docs/REQUIREMENTS.md 3.2 分镜脚本格式。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class Shot(BaseModel):
    id: str
    scene: str = ""
    camera: str = ""
    duration_sec: float | None = None
    prompt: str = ""
    negative_prompt: str = ""
    workflow: str = ""
    workflow_params: dict[str, Any] = Field(default_factory=dict)
    notes: str = ""


class Storyboard(BaseModel):
    project: str
    episode: str
    shots: list[Shot] = Field(default_factory=list)

    def shot_ids(self) -> list[str]:
        return [s.id for s in self.shots]


def load_storyboard(path: str | Path) -> Storyboard:
    """从yaml文件加载并校验分镜脚本，字段不合规会抛出 pydantic.ValidationError。"""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Storyboard.model_validate(data)


def validate_storyboard_file(path: str | Path) -> tuple[bool, str]:
    """返回 (是否通过, 提示信息)，供CLI友好展示，不抛异常。"""
    try:
        sb = load_storyboard(path)
    except Exception as e:  # noqa: BLE001 - 需要把各种解析/校验错误统一转成友好提示
        return False, f"校验失败: {e}"

    if not sb.shots:
        return False, "校验失败: shots 列表为空"

    ids = sb.shot_ids()
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        return False, f"校验失败: 镜头号重复: {sorted(dup)}"

    return True, f"校验通过: {sb.project}/{sb.episode}，共 {len(sb.shots)} 个镜头"
