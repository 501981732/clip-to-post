# Clip-to-Post Skill

[English README](./README.md)

![Skill](https://img.shields.io/badge/Codex%20Skill-Ready-2563eb?style=for-the-badge)
![Multimodal](https://img.shields.io/badge/Multimodal-Video%20%2B%20Images-10b981?style=for-the-badge)
![Workflow](https://img.shields.io/badge/Workflow-Human%20in%20the%20Loop-f59e0b?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Blueprint-111827?style=for-the-badge)

![Clip-to-Post hero](./assets/clip-to-post-hero.png)

**Clip-to-Post** 是一个可复用的 AI Workflow Skill，用来把视频、关键帧、截图或图片批量素材转成可发布的社媒内容包：故事板分镜、平台文案、封面图和可导出的工作流状态。

它不是“一个 Prompt 生成全部”的玩法，而是一条更稳定、可调试、可产品化的创作流水线：

```text
视频 / 图片素材
  -> 关键帧
  -> 步骤分析
  -> 基础故事板
  -> 角色 / 水印融合
  -> 单分镜精修
  -> 社媒文案
  -> 文案选择
  -> 封面生成
  -> 导出发布包
```

## 为什么值得做成 Skill

很多 AI 内容工具把所有任务压进一次模型调用里，结果是难调试、难复用，也很难接入真实产品。

Clip-to-Post 把内容生成拆成一条小型生产线：

- **先理解，再生成**：先把关键帧分析成结构化步骤。
- **先大图，再局部**：先生成完整故事板，再逐个精修分镜。
- **先内容，再封面**：先基于最终视觉内容写文案，再用选中文案生成封面。
- **平台策略可替换**：小红书、Instagram、SOP 文档、垂直场景都可以走不同 Strategy。
- **适合人工介入**：可以编辑步骤、锁定分镜、选择文案，只重跑受影响的下游节点。

## 适合场景

- AI 内容工厂
- 短视频二创 / 图文再创作工具
- 多模态 Workflow Demo
- Agent / Skill 市场
- 故事板生成
- 小红书 / Instagram 图文生成
- 产品教程和企业内部 SOP 可视化

## 仓库内容

```text
.
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── assets/
│   └── clip-to-post-hero.png
├── scripts/
│   └── extract_frames.py
└── references/
    ├── pipeline-blueprint.md
    ├── prompt-templates.md
    └── schemas.md
```

## 截帧能力边界

这个仓库现在补了一个**本地视频截帧脚本**，但它仍然不是万能网页视频播放器。

| 素材来源 | 当前仓库是否支持 | 说明 |
| --- | --- | --- |
| 本地 `.mp4`、`.mov`、`.mkv` 文件 | 支持，通过 `scripts/extract_frames.py` | 需要安装 `ffmpeg` 和 `ffprobe` |
| 已排序图片批量 / 截图 | 支持 | 可以直接作为 `FrameData[]` 输入 |
| 宿主 App 里已经能播放的视频 | 只提供契约 | 宿主应用需要用 `<video>` + `canvas.drawImage()` 实现 |
| B 站、Instagram、登录态页面、过期 URL、DRM/CORS 媒体 | 不直接支持 | 需要宿主浏览器/后端抽帧、代理、权限或平台专用工具 |

### `SKILL.md`

Skill 主入口，定义触发场景和分段式多模态工作流。

### `references/pipeline-blueprint.md`

从 ClipSketch Pipeline 蒸馏出的架构蓝图，包括节点职责、Provider 抽象、状态持久化、导出行为和失败处理。

### `references/prompt-templates.md`

步骤分析、故事板生成、角色融合、分镜精修、文案生成、封面生成的 Prompt 模板。

### `references/schemas.md`

输入、关键帧、步骤分析、产物、Pipeline 状态、模型 Provider、导出包的 TypeScript 风格契约。

## Pipeline

```mermaid
flowchart LR
  A["视频 / 图片批量"] --> B["关键帧提取"]
  B --> C["步骤分析"]
  C --> D["基础故事板"]
  D --> E["角色 / 水印融合"]
  E --> F["分镜精修"]
  F --> G["文案生成"]
  G --> H["文案选择"]
  H --> I["封面生成"]
  I --> J["导出发布包"]
```

## 快速开始

克隆仓库：

```bash
git clone https://github.com/501981732/clip-to-post.git
cd clip-to-post
```

可以直接把这个目录作为 Codex / Claude 兼容的 Skill 使用，也可以从干净 checkout 打包。

使用 skill creator 工具校验：

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py /path/to/clip-to-post
```

从 git checkout 生成干净的可分发 zip：

```bash
mkdir -p dist
git archive --format=zip --prefix=clip-to-post/ HEAD -o dist/clip-to-post.zip
```

抽取本地视频关键帧：

```bash
python3 scripts/extract_frames.py ./demo.mp4 --timestamps 0,2.5,5 --out ./frames --include-base64
```

或者按固定间隔抽帧：

```bash
python3 scripts/extract_frames.py ./demo.mp4 --every-seconds 2 --max-frames 8 --out ./frames
```

脚本会输出 JPEG 图片和 `manifest.json`。后续 Pipeline 可以把 manifest 里的 frames 作为视觉输入。

## 示例触发词

```text
使用 clip-to-post，把这些做菜视频帧转成小红书图文发布包。
```

```text
设计一个 AI 工作流，把产品教程截图转成故事板、文案和封面。
```

```text
把这段旅行视频改造成 Instagram 轮播图，并给我 3 个文案版本。
```

```text
把它当内部 SOP 生成器：分析截图，生成步骤图，并导出可落库的状态结构。
```

## 设计原则

- **小节点优于大 Prompt。**
- **中间产物必须可见、可编辑、可持久化。**
- **平台风格应该放在 Strategy 层，而不是散落在各个 Prompt 里。**
- **图片和文案应该来自同一份素材事实。**
- **重跑时只让受影响的下游节点失效。**

## 后续可以扩展

- 增加更多平台策略：抖音、微信、TikTok、YouTube Shorts。
- 增加更多垂直场景：宝宝成长、美食菜谱、健身动作、汽车测评、产品教程、旅行记录、内部 SOP。
- 增加示例 Workflow Runner。
- 增加 demo 发布包。
- 增加成本统计和模型路由参考文档。
- 增加面向宿主 App 的浏览器截帧适配器。

## 关键词

`ai-skill` `multimodal-ai` `agent-workflow` `video-to-post` `storyboard-generation` `content-repurposing` `prompt-engineering` `human-in-the-loop` `xiaohongshu` `instagram`
