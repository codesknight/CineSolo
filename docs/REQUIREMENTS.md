# CineSolo 需求文档

> 「一个人 + AI」完成影视全流程 —— 个人影视项目的生产流水线。
> 本文档记录项目的目标、范围与需求变更历史。每次需求变化都应在下方「变更记录」追加条目，不要直接删除旧内容。

## 1. 项目定位

- **项目性质**：个人使用的影视生产流水线（脚本 + AI 工作流），运行在自有服务器上，不是面向他人的通用产品。
- **核心理念**：一个人 + AI 覆盖影视制作全流程，用自动化/AI辅助替代传统需要多人协作完成的环节。
- **使用者**：项目所有者本人（liuyanhong0225@gmail.com / codesknight）。

## 2. 影视生产全流程

> 按典型影视生产流程列出阶段。✅已确认要优先自动化的阶段，其余阶段暂不在CineSolo当前范围内（不代表不做，只是不是第一批）。

1. 策划/立项 — 选题、大纲（暂不在范围）
2. 剧本 — 剧本生成/润色（暂不在范围，但是分镜的输入，需要有存放/读取约定）
3. **分镜** ✅ — 分镜脚本 → 批量驱动ComfyUI workflow，产出图像/视频素材（**第一优先级**）
4. 拍摄/素材获取（暂不在范围，AI生成素材由第3步产出）
5. **剪辑** ✅ — 把生成的素材自动拼剪成初剪（**第一优先级**）
6. 调色/特效（暂不在范围）
7. 配音/音乐/音效（暂不在范围，服务器已有IndexTTS/Qwen-TTS等语音节点，后续可能纳入）
8. 成片输出与归档（暂不在范围）

## 3. 功能需求

| 编号 | 需求描述 | 优先级 | 状态 | 备注 |
|------|----------|--------|------|------|
| REQ-001 | 分镜脚本批量转ComfyUI workflow，自动出图/出视频 | 高 | 🟢v1已实现（仅文生图） | `cinesolo render run <storyboard.yaml>`，用镜头的prompt/negative_prompt/workflow_params驱动ComfyUI的`workflows/txt2img_basic.json`模板（SD1.5文生图），已端到端验证成功。当前只支持这一个模板/一种生成方式（出图），出视频、支持更多workflow模板（Z-Image/Qwen-Image/Wan视频等）留待后续迭代 |
| REQ-002 | 将生成的素材按分镜顺序自动拼剪成初剪 | 高 | 待细化 | 用ffmpeg（服务器已有）做时间线拼接，转场/配乐等细节待定 |
| REQ-003 | 提供CLI工具，可命令行触发分镜生成/剪辑任务 | 高 | 待细化 | CLI为最小可用形态，优先落地 |
| REQ-004 | 提供Web界面，可视化管理项目/查看生成结果/触发任务 | 中 | 待细化 | 在CLI能跑通核心流程之后再做，作为CLI的上层界面 |
| REQ-005 | 项目/素材按"项目/集数/镜头号"目录规范存储在数据盘 | 高 | 待细化 | 见下方「4.1 目录规范」 |

## 3.1 目录规范（数据盘）

✅已确认：项目数据放 **`/root/autodl-tmp`**（不用`autodl-fs`）。

目录结构：

```
/root/autodl-tmp/CineSolo/projects/<项目名>/<集数>/<镜头号>/
  ├── storyboard.yaml   # 该镜头的结构化分镜脚本（见3.2）
  ├── generated/         # ComfyUI生成的图像/视频素材
  └── edit/              # 该镜头剪辑相关的中间文件
/root/autodl-tmp/CineSolo/projects/<项目名>/<集数>/output/   # 该集的初剪/成片输出
```

*(具体字段命名、镜头号编码规则，随脚手架代码落地，后续如需调整在此更新)*

## 3.2 分镜脚本格式

✅已确认：用**结构化格式（YAML）**，而不是纯文字描述。每一集一个 `storyboard.yaml`，包含该集所有镜头：

```yaml
project: "示例项目"
episode: "E01"
shots:
  - id: "S001"
    scene: "场景描述，例如：雨夜街道，霓虹灯反光"
    camera: "运镜方式，例如：缓慢推近"
    duration_sec: 4
    prompt: "AI生成用的正向提示词"
    negative_prompt: ""          # 可选，负向提示词
    workflow: "wan_video_t2v"     # 引用的ComfyUI workflow模板名（后续在workflow模板库中定义）
    workflow_params: {}           # 该镜头需要覆盖的workflow参数，可选
    notes: ""                     # 备注，可选
  - id: "S002"
    ...
```

*(字段随REQ-001实现细化调整，后续变更记在本文档变更记录)*

## 4. 非功能需求

- 运行环境：远程GPU服务器（见 [开发文档](DEVLOG.md) 环境章节）
- 其他约束：待补充

## 5. 技术选型

- **AI生成引擎**：✅已确认——基于服务器上现有的 **ComfyUI**（RTX 5090，已装40+自定义节点，覆盖视频生成/超分/换脸/打光/语音合成/标注等，装在`/root/autodl-tmp/ComfyUI`）。CineSolo定位为在ComfyUI能力之上做**工作流编排/自动化层**（串联剧本→分镜→生成→剪辑，减少手动操作ComfyUI），不重新实现底层生成能力（详见 [开发文档 - 已部署的AI工具](DEVLOG.md#已部署的ai工具这是最关键的部分服务器上已经有一套相当完整的ai影视生产工具链而非空白环境)）
- **ComfyUI启动**：`source ~/miniconda3/etc/profile.d/conda.sh && conda activate base && cd /root/LaunchTool311 && python startup.py --hf-mirror --proxy-on --port=6006 --preview-method=latent2rgb --preview-size=256`，启动后HTTP API在`http://127.0.0.1:6006`（仅本机可访问）
- **ComfyUI API**（已实测可用）：`GET /system_stats`（系统/GPU状态）、`GET /object_info/<节点名>`（查询节点参数定义，用于程序化拼装workflow）、`POST /prompt`（提交生成任务，标准方式）、`GET /history/<prompt_id>`或websocket（查询任务结果）——这是REQ-001要用的核心接口
- **运行环境**：AutoDL云GPU服务器，Python 3.11 (miniconda)，ffmpeg已具备
- **存储约定**：项目产出物（模型、生成的素材/中间文件等）一律放**数据盘 `/root/autodl-tmp`**，不放系统盘（系统盘仅30G，空间紧张），见 3.1 目录规范
- **交互方式**：✅已确认——CLI + Web 都要。落地顺序：先做CLI打通核心流程（分镜自动化+剪辑自动化），再在CLI之上包一层Web
- 其他（编排语言/框架、任务队列、剧本的存储格式细节）：待确定，倾向Python（与ComfyUI/现有环境一致）

## 6. 变更记录

| 日期 | 变更内容 | 说明 |
|------|----------|------|
| 2026-09-07 | 创建需求文档骨架 | 项目定位确认为「个人影视项目的生产流水线」，具体流程阶段待细化 |
| 2026-09-07 | 补充技术选型初判 | 勘查远程服务器后发现已预装ComfyUI全套AI生成工具链，初判CineSolo为ComfyUI之上的工作流编排层，待用户确认 |
| 2026-09-07 | 用户确认技术方向 | 确认CineSolo=ComfyUI之上的工作流编排/自动化层；补充存储约定（产出物放数据盘，不放系统盘） |
| 2026-09-07 | 确定第一优先级范围 | 优先自动化「分镜」「剪辑」两个环节；交互方式CLI+Web（先CLI后Web）；补充REQ-001~005及目录规范草案 |
| 2026-09-07 | 固化目录规范与分镜格式 | 数据盘选定`/root/autodl-tmp`；分镜脚本格式确认为结构化YAML（storyboard.yaml），开始写最小CLI代码脚手架 |
| 2026-09-07 | 打通ComfyUI启动与API | 用户扩容磁盘后确认`autodl-tmp`可用；找到并验证了ComfyUI启动命令与HTTP API（system_stats/object_info/prompt/history），为REQ-001实现打下基础 |
| 2026-09-07 | REQ-001 v1（文生图）端到端跑通 | 用镜像自带的90个开源workflow之一（SD图像系列-SD15简单文生图，用现有anything-v5模型，零额外下载）做成`workflows/txt2img_basic.json`模板；实现`cinesolo render run`；在服务器上实测生成成功 |
