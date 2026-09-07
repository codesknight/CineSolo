# CineSolo Bug / 测试记录

> 记录测试过程中发现的问题、复现步骤、修复状态。新条目追加在表格底部，编号递增，已修复的不要删除，改状态为「已修复」。

## 状态说明

- 🔴 待处理
- 🟡 处理中
- 🟢 已修复
- ⚪ 已关闭（不修复/无法复现/非问题）

## 记录列表

| 编号 | 日期 | 描述 | 复现步骤 | 严重程度 | 状态 | 修复说明/关联提交 |
|------|------|------|----------|----------|------|------|
| BUG-001 | 2026-09-07 | Windows终端下`cinesolo`命令输出中文乱码 | 在Windows默认codepage（非UTF-8）的终端下运行`cinesolo storyboard validate ...`等含中文输出的命令 | 低 | 🟢已修复 | 只是终端显示问题，不影响文件系统里的实际数据（UTF-8写入正常）。目标运行环境是Linux服务器（UTF-8 locale），本不会复现；仍在`cli.py`加了`stdout/stderr.reconfigure(encoding="utf-8")`做防御性修复，Windows下终端还需自行`chcp 65001`配合 |
| BUG-002 | 2026-09-07 | 远程服务器实际没有独立可写数据盘，`/root/autodl-tmp`只是系统盘上的普通目录；`/root/autodl-fs`符号链接目标也不存在（未挂载/不可写） | 登录服务器执行`df -h`/`mount`/`lsblk`核实（见docs/DEVLOG.md"2026-09-07更正"）；`touch /root/autodl-fs/.write_test`报错"No such file or directory" | 中 | 🟢已缓解 | 用户在AutoDL控制台手动扩容，系统盘从30G→79G（剩57G）。`autodl-tmp`和系统盘技术上仍是同一文件系统（非物理独立盘），但容量已够当前阶段使用，且确认是该AutoDL镜像的标准数据存放位置（ComfyUI本身也装在`/root/autodl-tmp/ComfyUI`下）。后续如果视频生成素材持续堆积导致空间告急，需要重新评估（真正的解法可能是另购/挂载独立数据盘，或定期把成片/素材搬出服务器归档） |

## 测试记录

> 非缺陷类的测试观察、验证结果，可记录在此处。

- 2026-09-07：项目初始化，暂无可测试内容
- 2026-09-07：CLI最小脚手架本地验证（Windows开发机）——`pytest`4项测试全过；`cinesolo storyboard validate`、`cinesolo project init-from-storyboard`手动跑通，生成的目录结构符合预期（见docs/REQUIREMENTS.md 3.1）。尚未在远程服务器（实际运行环境）上验证
