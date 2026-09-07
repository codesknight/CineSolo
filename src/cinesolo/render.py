"""REQ-001：分镜脚本批量转ComfyUI workflow，自动出图。

v1只支持 workflows/txt2img_basic.json 这一个模板（SD1.5简单文生图，见该文件），
节点id写死在 TXT2IMG_BASIC_NODES 里——后续要支持更多workflow模板时再抽象成配置。
"""

from __future__ import annotations

import copy
import json
import random
from pathlib import Path
from typing import Any

from cinesolo.comfyui_client import ComfyUIClient
from cinesolo.storyboard import Shot, Storyboard

DEFAULT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent / "workflows" / "txt2img_basic.json"

# txt2img_basic.json 里各功能对应的节点id
TXT2IMG_BASIC_NODES = {
    "checkpoint": "4",
    "positive": "6",
    "negative": "7",
    "latent": "5",
    "sampler": "3",
}


def load_template(path: str | Path = DEFAULT_TEMPLATE_PATH) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def build_workflow_for_shot(template: dict[str, Any], shot: Shot) -> dict[str, Any]:
    """把模板复制一份，用镜头的prompt/negative_prompt/workflow_params覆盖对应节点。"""
    wf = copy.deepcopy(template)
    nodes = TXT2IMG_BASIC_NODES

    if shot.prompt:
        wf[nodes["positive"]]["inputs"]["text"] = shot.prompt
    if shot.negative_prompt:
        wf[nodes["negative"]]["inputs"]["text"] = shot.negative_prompt

    params = shot.workflow_params or {}
    if "width" in params:
        wf[nodes["latent"]]["inputs"]["width"] = params["width"]
    if "height" in params:
        wf[nodes["latent"]]["inputs"]["height"] = params["height"]
    if "ckpt_name" in params:
        wf[nodes["checkpoint"]]["inputs"]["ckpt_name"] = params["ckpt_name"]

    seed = params.get("seed")
    if seed is None:
        seed = random.randint(0, 2**32 - 1)
    wf[nodes["sampler"]]["inputs"]["seed"] = seed

    wf[nodes["sampler"]]["inputs"]["filename_prefix"] = shot.id
    # SaveImage节点id目前固定是"9"，和采样器分开处理文件名前缀
    if "9" in wf:
        wf["9"]["inputs"]["filename_prefix"] = f"cinesolo_{shot.id}"

    return wf


def render_shot(
    client: ComfyUIClient,
    shot: Shot,
    output_dir: Path,
    template: dict[str, Any] | None = None,
    timeout: float = 300,
) -> list[Path]:
    """驱动ComfyUI为单个镜头生成图片，保存到output_dir，返回保存的文件路径列表。"""
    if template is None:
        template = load_template()

    workflow = build_workflow_for_shot(template, shot)
    prompt_id = client.submit_prompt(workflow)
    history_entry = client.wait_for_result(prompt_id, timeout=timeout)

    status = history_entry.get("status", {})
    if status.get("status_str") == "error":
        raise RuntimeError(f"镜头 {shot.id} 生成失败: {status}")

    images = client.extract_images(history_entry)
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    for i, img in enumerate(images):
        data = client.fetch_image(img["filename"], img.get("subfolder", ""), img.get("type", "output"))
        ext = Path(img["filename"]).suffix or ".png"
        out_path = output_dir / f"{shot.id}_{i}{ext}"
        out_path.write_bytes(data)
        saved_paths.append(out_path)

    return saved_paths


def render_storyboard(
    storyboard: Storyboard,
    get_shot_generated_dir,
    base_url: str = "http://127.0.0.1:6006",
    template_path: str | Path = DEFAULT_TEMPLATE_PATH,
    timeout: float = 300,
) -> dict[str, list[Path]]:
    """驱动ComfyUI为storyboard里所有镜头批量生成图片。

    get_shot_generated_dir: (shot_id) -> Path，由调用方提供每个镜头素材应存放的目录
    （通常是 cinesolo.project 里算出来的 <episode_dir>/<shot_id>/generated）。
    """
    client = ComfyUIClient(base_url=base_url)
    template = load_template(template_path)

    results: dict[str, list[Path]] = {}
    for shot in storyboard.shots:
        out_dir = get_shot_generated_dir(shot.id)
        results[shot.id] = render_shot(client, shot, out_dir, template=template, timeout=timeout)
    return results
