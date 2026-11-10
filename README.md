# slides-digital-notebook

A Claude skill for building, auditing and explaining tabbed "digital notebooks" in Google Slides.
See `SKILL.md`.

## Install (Claude Code)

```bash
git clone https://github.com/scerruti/slides-digital-notebook-skill.git ~/.claude/skills/slides-digital-notebook
```

Update: `git -C ~/.claude/skills/slides-digital-notebook pull`

Needs Python 3 (standard library only), the Google Slides/Drive connectors, and the `google-workspace` skill.

## Package for claude.ai

```bash
cd ~/.claude/skills && zip -r ~/Desktop/slides-digital-notebook.skill slides-digital-notebook -x '*/.git/*' '*/__pycache__/*' '*.DS_Store'
```

Upload under Settings → Capabilities → Skills.
