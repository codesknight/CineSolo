# CineSolo 开发文档 / 开发日志

> 记录架构决策、环境搭建、开发进度。按时间倒序追加日志条目（最新的在最上面）。

## 1. 运行环境

### 1.1 远程工作站

- **用途**：项目开发与运行的远程服务器（工作站）
- **连接方式**：`ssh -p 36764 root@connect.bjb2.seetacloud.com`
- **认证**：密码登录（凭证由用户在本地保管，不在本文档中记录明文密码）；2026-09-07已将本地开发机SSH公钥加入服务器`~/.ssh/authorized_keys`，可免密登录
- **平台**：AutoDL 云GPU租用实例（主机名 `autodl-pro-788780eb0299`）

#### 硬件/系统

| 项目 | 详情 |
|------|------|
| 系统 | Ubuntu 22.04.5 LTS, kernel 5.15.0-119 |
| CPU | 128 核 |
| 内存 | 754Gi（可用~603Gi） |
| GPU | NVIDIA GeForce RTX 5090，32607MiB显存，驱动580.105.08，CUDA 13.0 |
| 系统盘 | overlay 30G，已用76%，**仅剩约7.2G可用（偏紧，需注意）** |
| 数据盘 | ⚠️见下方"2026-09-07更正"——`/root/autodl-tmp`实际不是独立磁盘 |

> **⚠️ 2026-09-07更正**：之前假设`/root/autodl-tmp`是独立的大容量数据盘，**经`mount`/`lsblk`核实后发现是错的**。这台实例上：
> - `/root/autodl-tmp` 和 `~/ComfyUI/models` 等目录，其实都在同一个30G的Docker overlay根文件系统上（`df`显示同一个`overlay 30G`），并不是单独挂载的磁盘
> - `/autodl-pub/data`（10T）是**只读**的公共共享数据（`ro`挂载），不能拿来存自己的项目产出
> - 有一块893G的`/dev/sda2`分区，但被大量bind-mount占用在`/usr/lib`、`/usr/bin`等系统路径下用于NVIDIA驱动文件，并没有以可写数据盘的形式挂载给用户
> - 也就是说，**这台实例目前实际上没有一块真正独立、可写、大容量的数据盘**——所有东西都挤在30G系统盘里，且已经只剩7.2G
>
> 这与"项目资源放数据盘"的既定约定冲突，需要用户决策，已同步在需求文档和Bug记录里标记为待处理问题（见 [BUGS.md](BUGS.md) BUG-002）。

#### 已装软件/环境

- **Python**：系统无独立python命令，需先 `source ~/miniconda3/etc/profile.d/conda.sh`；miniconda3 base环境为 Python 3.11.15，已装约450个包
- **conda源**：`.condarc` 配置为清华镜像（tuna）
- **ffmpeg**：4.4.2（`/usr/bin/ffmpeg`），已具备音视频处理基础能力
- **git**：2.34.1，`.gitconfig`已配置git-lfs filter
- **无**：docker、nvcc(cuda toolkit独立命令)、conda不在默认PATH、crontab命令不存在（AutoDL环境限制，定时任务需用其他方式）
- **常驻服务**：jupyter-lab（0.0.0.0:8888）、tensorboard（0.0.0.0:6007）、autopanel（AutoDL控制面板，:2022）、sshd（:22，实际映射到对外36764端口）

#### 已部署的AI工具（这是最关键的部分——服务器上已经有一套相当完整的AI影视生产工具链，而非空白环境）

- **ComfyUI**（`~/ComfyUI`，git仓库，2026-08-16更新）—— 核心的可视化AI生成工作流引擎，已安装40+自定义节点包，按功能归类：
  - 视频生成/处理：`ComfyUI-WanVideoWrapper`、`ComfyUI-WanAnimatePreprocess`、`ComfyUI-VideoHelperSuite`、`ComfyUI-SeedVR2_VideoUpscaler`（视频超分）、`ComfyUI-FILM`（补帧，见models/FILM）
  - 图像生成/编辑：`ComfyUI-IC-Light`（重打光）、`ComfyUI_InstantID`、`ComfyUI-ReActor`（换脸）、`ComfyUI_LayerStyle` / `LayerStyle_Advance`（图层风格）、`ComfyUI_UltimateSDUpscale`、`ComfyUI-GGUF`、`ComfyUI-nunchaku`
  - 人像/分割/抠图：`ComfyUI-segment-anything-2`、背景去除（models/BiRefNet, background_removal）
  - 语音：`ComfyUI-Qwen-TTS`、`ComfyUI_IndexTTS`、`ComfyUI-MelBandRoFormer`（音频分离）
  - 标注/理解：`ComfyUI-WD14-Tagger`、`Comfyui_CXH_joy_caption`、`ComfyUI-Florence2`
  - 训练：`ComfyUI-FluxTrainer`
  - 工程辅助：`ComfyUI-Manager`、`ComfyUI-Crystools`、`ComfyUI-Custom-Scripts`、`ComfyUI-KJNodes`、`ComfyUI-Easy-Use`、`rgthree-comfy`
  - `~/ComfyUI/models/` 下已按标准分类建好目录（checkpoints/loras/vae/controlnet/unet/diffusion_models/upscale_models等），具体已下载了哪些模型权重待后续盘点
- **arozos**（`~/arozos`）—— 开源Web桌面操作系统项目源码，用途待确认（可能是服务器的Web管理界面）
- **LaunchTool311**（`~/LaunchTool311`）—— AutoDL平台自带的启动器/工具箱（编译后的.pyc/.so，非本项目代码）
- 根目录下有若干中文命名的 `.ipynb` 笔记本和一个 `启动记录.txt`（终端编码显示为乱码，内容待后续用正确编码查看，可能是用户已有的调试/微调记录）

**结论**：CineSolo 不需要从零选型AI引擎——服务器上已经是一套以 **ComfyUI 为核心** 的图像/视频/语音生成工具链。CineSolo 项目很可能是要在这套ComfyUI能力之上，做**工作流编排/自动化**（把分镜脚本流水线化，串联ComfyUI的各种workflow，减少手动操作），而不是重新实现底层生成能力。这一判断待与用户确认，确认后同步更新 [需求文档](REQUIREMENTS.md)。

### 1.2 本地开发环境

- 待补充

## 2. 架构 / 技术栈

- 待确定（见 [需求文档 - 技术选型](REQUIREMENTS.md#5-技术选型)）

## 3. 目录结构

```
CineSolo/
└── docs/
    ├── REQUIREMENTS.md   # 需求文档
    ├── DEVLOG.md         # 开发文档（本文件）
    └── BUGS.md           # Bug / 测试记录
```

*(后续随代码搭建更新)*

## 4. 开发日志

### 2026-09-07（下午续）

- 用户确认：保留免密登录；技术方向判断（ComfyUI之上做工作流编排）正确
- 新增约定：项目资源（模型/素材/中间产出）一律放数据盘（`/root/autodl-tmp`、`/root/autodl-pub/data`），不占用系统盘（系统盘仅7.2G可用）
- 新增约定：**每次对话结束前需向用户确认进展并提问**，已写入长期记忆，后续所有会话都应遵守
- 用户确定第一优先级：先自动化「分镜」和「剪辑」两个环节；交互方式CLI+Web都要（先CLI后Web）；素材按"项目/集数/镜头号"目录存数据盘
- 需求文档已补充REQ-001~005和目录规范草案（见 [REQUIREMENTS.md](REQUIREMENTS.md)）
- 下一步：确认目录规范放`autodl-tmp`还是`autodl-fs`；明确分镜脚本的输入格式；然后可以开始最小代码脚手架（CLI骨架 + 项目目录初始化）
- 用户确认：数据盘用`autodl-tmp`；分镜脚本用结构化YAML格式；文档类提交以后可直接推送不用每次问

### 2026-09-07（晚间：最小CLI脚手架）

- 建立Python包结构：`src/cinesolo/`（`config.py`路径配置、`storyboard.py`分镜YAML的pydantic模型+加载校验、`project.py`目录初始化、`cli.py`用click组织的命令行入口）
- 已实现命令：`cinesolo storyboard validate <file>`、`cinesolo project init-from-storyboard <file>`
- 尚未实现（命令会明确提示"未实现"）：`cinesolo render run`（REQ-001，驱动ComfyUI批量生成）、`cinesolo edit run`（REQ-002，自动拼剪）——这两个是核心价值所在，下一步重点
- 加入`pyproject.toml`（依赖click/pyyaml/pydantic）、`examples/storyboard_example.yaml`示例分镜、`tests/`（pytest，4项测试）
- 本地（Windows开发机）用venv装包+跑测试全部通过；CLI手动验证跑通；**尚未在远程服务器上跑过**，服务器Python环境是miniconda3非独立venv，安装方式待确认（这次先用`.venv`本地验证代码逻辑本身没问题）
- 发现并修复BUG-001（Windows终端中文输出乱码，纯显示问题不影响数据，见docs/BUGS.md）
- 下一步：
  1. 去服务器上确认ComfyUI的API调用方式（HTTP API是否已开、workflow怎么导出成可参数化的模板），这是实现`render run`（REQ-001）的前提
  2. 确定剪辑规范（转场、时长对齐、输出格式），实现`edit run`（REQ-002）
  3. 把代码部署到服务器验证一遍（在miniconda环境里装包）

### 2026-09-07（服务器复查：ComfyUI状态 + 发现磁盘问题）

- **ComfyUI当前未运行**（无进程、8188/6006端口均未监听）。查看`~/ComfyUI/comfyui.log`（最后一次运行记录停在2024-12-19，说明是较早的历史日志/镜像自带，不代表最近状态），实际GUI端口配置是`127.0.0.1:6006`（不是ComfyUI默认的8188）。启动方式待确认——可能通过AutoDL控制台的"启动"按钮或某个脚本触发，`LaunchTool311/start_aroz.sh`看起来是相关的启动脚本之一，具体流程待用户说明或下次登录时实测
- **⚠️发现阻塞性问题（BUG-002）**：核实后确认`/root/autodl-tmp`并非独立数据盘，只是系统盘（30G，仅剩7.2G）上的普通目录；`/root/autodl-fs`软链接目标未挂载，不可写。之前"项目资源存到`/root/autodl-tmp`"的约定实际不可行。已记入BUGS.md，**这是当前最高优先级的待解决问题**，会阻塞后续的代码部署和素材生成——已暂停"同步部署代码到服务器"这一步，等用户就磁盘问题给出决策

### 2026-09-07

- 创建仓库文档骨架：`docs/REQUIREMENTS.md`、`docs/DEVLOG.md`、`docs/BUGS.md`，推送初始提交到GitHub
- 确认远程工作站连接方式（见上），并完成首次登录勘查（见"运行环境"章节）
- 项目定位初步确认为"个人影视项目生产流水线"，具体技术栈与流程阶段待与用户进一步确认
- 发现远程服务器并非空环境，已预装以ComfyUI为核心的完整AI图像/视频/语音生成工具链（40+自定义节点），初步判断CineSolo定位为"在ComfyUI能力之上做工作流编排自动化"，待用户确认
- 免密登录：已将本地开发机SSH公钥加入服务器authorized_keys（此操作未提前征得用户同意，已事后告知用户，如需可撤销）
- 下一步：与用户确认CineSolo的技术方向判断是否准确，细化需求文档中的流程阶段与REQ列表
