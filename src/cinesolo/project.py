"""项目/集数/镜头 目录初始化。

目录规范见 docs/REQUIREMENTS.md 3.1。
"""

from __future__ import annotations

from pathlib import Path

from cinesolo.config import get_episode_dir
from cinesolo.storyboard import Storyboard


def init_episode(project: str, episode: str) -> Path:
    """创建 <project>/<episode>/output 目录，返回该集目录路径。"""
    episode_dir = get_episode_dir(project, episode)
    (episode_dir / "output").mkdir(parents=True, exist_ok=True)
    return episode_dir


def init_shots_from_storyboard(storyboard: Storyboard) -> list[Path]:
    """按storyboard里的镜头列表，在对应集数目录下创建每个镜头的子目录
    （storyboard.yaml所在集目录 / 镜头号 / generated, edit）。

    返回创建的镜头目录列表。
    """
    episode_dir = init_episode(storyboard.project, storyboard.episode)
    shot_dirs = []
    for shot in storyboard.shots:
        shot_dir = episode_dir / shot.id
        (shot_dir / "generated").mkdir(parents=True, exist_ok=True)
        (shot_dir / "edit").mkdir(parents=True, exist_ok=True)
        shot_dirs.append(shot_dir)
    return shot_dirs
