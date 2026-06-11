# Clip-to-Post Skill

`clip-to-post` is a reusable AI workflow skill distilled from the ClipSketch AI pipeline. It turns video clips, keyframes, screenshots, or image batches into a structured social-media content package:

```text
visual material
  -> keyframe normalization
  -> step analysis
  -> storyboard generation
  -> character/watermark integration
  -> panel refinement
  -> caption generation
  -> cover generation
  -> exportable workflow state
```

The skill is designed for human-in-the-loop multimodal content production, not for a single giant prompt. Each pipeline node owns one task and produces inspectable intermediate artifacts.

## Structure

```text
.
├── SKILL.md
└── references/
    ├── pipeline-blueprint.md
    ├── prompt-templates.md
    └── schemas.md
```

## Use Cases

- Build a "video/images to social post" content workflow.
- Productize a multimodal AI content factory.
- Create a Workshop or workflow-engine demo with visible state transitions.
- Reuse ClipSketch-style prompts, state contracts, and platform strategies.

## Packaging

From the parent directory, run the skill packager:

```bash
python3 /path/to/skill-creator/scripts/package_skill.py clip-to-post ./dist
```

The package should contain `clip-to-post/SKILL.md` and the `references/` files.
