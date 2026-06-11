# Clip-to-Post Skill

[中文说明](./README.zh-CN.md)

![Skill](https://img.shields.io/badge/Codex%20Skill-Ready-2563eb?style=for-the-badge)
![Multimodal](https://img.shields.io/badge/Multimodal-Video%20%2B%20Images-10b981?style=for-the-badge)
![Workflow](https://img.shields.io/badge/Workflow-Human%20in%20the%20Loop-f59e0b?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Blueprint-111827?style=for-the-badge)

![Clip-to-Post hero](./assets/clip-to-post-hero.png)

**Clip-to-Post** is a reusable AI workflow skill for turning visual material into publish-ready social content: storyboard panels, captions, cover art, and exportable workflow state.

It is not a "one prompt does everything" trick. It distills a more reliable creative pipeline:

```text
video / images
  -> keyframes
  -> step analysis
  -> base storyboard
  -> character + watermark integration
  -> refined panels
  -> social captions
  -> cover art
  -> export package
```

## Why It Matters

Most AI content tools collapse everything into one giant model call. That is hard to debug, hard to steer, and hard to productize.

Clip-to-Post treats content generation like a small production line:

- **Understand before generating**: analyze keyframes into semantic steps first.
- **Draft before polishing**: generate the whole storyboard, then refine panels one by one.
- **Write from final visuals**: generate captions after the images exist.
- **Design for platforms**: use strategy prompts for Xiaohongshu, Instagram, SOP docs, and custom channels.
- **Keep humans in the loop**: allow editing steps, locking panels, selecting captions, and rerunning only stale nodes.

## Best For

- AI content factories
- Short-video repurposing tools
- Multimodal workflow demos
- Agent / Skill marketplaces
- Storyboard generation
- Xiaohongshu and Instagram post generation
- Product tutorials and internal SOP visual guides

## What Is Inside

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

## Frame Extraction Reality Check

This skill now includes a **local video frame extraction helper**, but it still does not magically play every video on the internet.

| Source | Supported by this repo | Notes |
| --- | --- | --- |
| Local `.mp4`, `.mov`, `.mkv` files | Yes, via `scripts/extract_frames.py` | Requires `ffmpeg` and `ffprobe` |
| Ordered image batches / screenshots | Yes | Use images directly as `FrameData[]` |
| Browser video already loaded in a host app | Contract only | Host app should use `<video>` + `canvas.drawImage()` |
| Bilibili, Instagram, logged-in pages, expiring URLs, DRM/CORS media | Not directly | Requires host browser/backend extraction, proxy, permissions, or platform-specific tooling |

### `SKILL.md`

The main skill entrypoint. It defines when to use the skill and how to execute the segmented multimodal workflow.

### `references/pipeline-blueprint.md`

The ClipSketch-inspired pipeline architecture: node responsibilities, provider abstraction, state persistence, export behavior, and failure handling.

### `references/prompt-templates.md`

Reusable prompt templates for step analysis, storyboard generation, character integration, panel refinement, caption generation, and cover generation.

### `references/schemas.md`

TypeScript-style contracts for input, frame data, step analysis, artifacts, pipeline state, provider interfaces, and export payloads.

## Pipeline

```mermaid
flowchart LR
  A["Video / Image Batch"] --> B["Keyframe Capture"]
  B --> C["Step Analysis"]
  C --> D["Base Storyboard"]
  D --> E["Character / Watermark"]
  E --> F["Panel Refinement"]
  F --> G["Caption Generation"]
  G --> H["Caption Selection"]
  H --> I["Cover Generation"]
  I --> J["Export Package"]
```

## Quick Start

Clone the repository:

```bash
git clone https://github.com/501981732/clip-to-post.git
cd clip-to-post
```

Use the skill folder directly in a Codex/Claude-compatible skill environment, or package it from a clean checkout.

Validate with the skill creator tooling:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py /path/to/clip-to-post
```

Create a clean distributable zip from the git checkout:

```bash
mkdir -p dist
git archive --format=zip --prefix=clip-to-post/ HEAD -o dist/clip-to-post.zip
```

Extract local video frames:

```bash
python3 scripts/extract_frames.py ./demo.mp4 --timestamps 0,2.5,5 --out ./frames --include-base64
```

Or sample at intervals:

```bash
python3 scripts/extract_frames.py ./demo.mp4 --every-seconds 2 --max-frames 8 --out ./frames
```

The script writes JPEG frames and `manifest.json`. Use the manifest frames as the visual input for the rest of the pipeline.

## Example Trigger Prompts

```text
Use clip-to-post to turn these cooking video frames into a Xiaohongshu post package.
```

```text
Design an AI workflow that converts product tutorial screenshots into storyboard panels, captions, and cover art.
```

```text
Repurpose this travel video into Instagram carousel panels with three caption options.
```

```text
Use this as an internal SOP generator: analyze screenshots, produce visual steps, and export an implementation-ready state schema.
```

## Design Principles

- **Small AI nodes beat giant prompts.**
- **Intermediate artifacts should be visible, editable, and persisted.**
- **Platform strategy belongs in a strategy layer, not scattered across prompts.**
- **Generated images and captions should share the same source truth.**
- **Reruns should invalidate only downstream artifacts.**

## Roadmap Ideas

- Add more platform strategies: Douyin, WeChat, TikTok, YouTube Shorts.
- Add domain strategies: baby memory, food recipe, fitness movement, auto review, product tutorial, travel log, internal SOP.
- Add a sample workflow runner.
- Add exported demo packages.
- Add cost and model-routing reference docs.
- Add browser extraction adapters for host apps that can legally access remote video playback.

## Keywords

`ai-skill` `multimodal-ai` `agent-workflow` `video-to-post` `storyboard-generation` `content-repurposing` `prompt-engineering` `human-in-the-loop` `xiaohongshu` `instagram`
