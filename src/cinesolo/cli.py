"""CineSolo 命令行入口。

当前是最小脚手架：项目目录初始化 + 分镜脚本校验。
批量驱动ComfyUI出图/出视频（REQ-001）和自动拼剪（REQ-002）尚未实现，
对应命令会明确提示"未实现"，而不是假装能跑。
"""

from __future__ import annotations

import sys

import click

# Windows控制台默认编码常常不是UTF-8，会导致中文输出乱码（不影响文件系统里的实际
# 数据，纯粹是终端显示问题）。Python 3.7+的stdout/stderr支持reconfigure，这里尽量
# 切到UTF-8；某些非标准终端可能不支持reconfigure，失败就忽略。见 docs/BUGS.md BUG-001。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass

from cinesolo import __version__
from cinesolo.config import get_data_root
from cinesolo.project import init_shots_from_storyboard
from cinesolo.storyboard import load_storyboard, validate_storyboard_file


@click.group()
@click.version_option(__version__, prog_name="cinesolo")
def main() -> None:
    """CineSolo —— 「一个人 + AI」影视生产流水线编排工具。"""


@main.group()
def storyboard() -> None:
    """分镜脚本相关命令。"""


@storyboard.command("validate")
@click.argument("path", type=click.Path(exists=True))
def storyboard_validate(path: str) -> None:
    """校验一个 storyboard.yaml 文件格式是否合规。"""
    ok, message = validate_storyboard_file(path)
    click.echo(message)
    if not ok:
        sys.exit(1)


@main.group()
def project() -> None:
    """项目/集数/镜头 目录管理命令。"""


@project.command("init-from-storyboard")
@click.argument("path", type=click.Path(exists=True))
def project_init_from_storyboard(path: str) -> None:
    """读取 storyboard.yaml，在数据盘上为该集及其所有镜头创建目录结构。"""
    ok, message = validate_storyboard_file(path)
    if not ok:
        click.echo(message)
        sys.exit(1)

    sb = load_storyboard(path)
    shot_dirs = init_shots_from_storyboard(sb)
    click.echo(f"已在 {get_data_root()} 下创建 {sb.project}/{sb.episode}，共 {len(shot_dirs)} 个镜头目录：")
    for d in shot_dirs:
        click.echo(f"  - {d}")


@main.group()
def render() -> None:
    """分镜批量生成（驱动ComfyUI）。对应需求文档 REQ-001，尚未实现。"""


@render.command("run")
@click.argument("path", type=click.Path(exists=True))
def render_run(path: str) -> None:
    """驱动ComfyUI，按storyboard批量生成每个镜头的素材。"""
    click.echo("尚未实现：批量驱动ComfyUI出图/出视频 (REQ-001)。")
    click.echo("需要先确定：如何通过API调用ComfyUI（HTTP API/websocket）、workflow模板怎么定义与参数化。")
    sys.exit(2)


@main.group()
def edit() -> None:
    """素材自动拼剪。对应需求文档 REQ-002，尚未实现。"""


@edit.command("run")
@click.argument("path", type=click.Path(exists=True))
def edit_run(path: str) -> None:
    """把已生成的素材按分镜顺序自动拼剪成初剪。"""
    click.echo("尚未实现：素材自动拼剪 (REQ-002)。")
    click.echo("需要先确定：转场/时长对齐规则、输出格式/分辨率等剪辑规范。")
    sys.exit(2)


if __name__ == "__main__":
    main()
