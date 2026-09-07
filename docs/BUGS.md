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
| BUG-002 | 2026-09-07 | 远程服务器实际没有独立可写数据盘，`/root/autodl-tmp`只是系统盘上的普通目录；`/root/autodl-fs`符号链接目标也不存在（未挂载/不可写） | 登录服务器执行`df -h`/`mount`/`lsblk`核实（见docs/DEVLOG.md"2026-09-07更正"）；`touch /root/autodl-fs/.write_test`报错"No such file or directory" | **高（阻塞性）** | 🔴待处理 | 与用户已确认的"项目资源存放数据盘"约定冲突——系统盘总共30G已剩7.2G，视频/图像生成的产出物很快会把它填满；`autodl-fs`网盘当前也没挂载，不能用。需要用户决策：①去AutoDL控制台检查/挂载数据盘或网盘（`autodl-fs`常见需要在控制台单独开通网盘服务） ②或接受当前小容量，靠及时清理/搬运素材维持。在此问题解决前不建议往服务器上堆放大量生成素材，也暂不适合部署代码到服务器（担心`pip install`等操作把仅剩7.2G占满） |

## 测试记录

> 非缺陷类的测试观察、验证结果，可记录在此处。

- 2026-09-07：项目初始化，暂无可测试内容
- 2026-09-07：CLI最小脚手架本地验证（Windows开发机）——`pytest`4项测试全过；`cinesolo storyboard validate`、`cinesolo project init-from-storyboard`手动跑通，生成的目录结构符合预期（见docs/REQUIREMENTS.md 3.1）。尚未在远程服务器（实际运行环境）上验证
