# learn

[![video](assets/thumbnail.png)](https://www.youtube.com/watch?v=kzcI5F4tGiU)

My AI learning system from this video: [How I Use AI to Learn Things](https://www.youtube.com/watch?v=kzcI5F4tGiU).

This is a personal system Amos built for himself, originally a [pi](https://github.com/earendil-works/pi) config. This fork is ported to **Claude Code**, so it runs on your Claude subscription limits.

## What's in it

- `skills/teach/`: the teaching philosophy and process (probe → plan → teach)
- `skills/visualize/`: adds a correct, minimal diagram to a lesson when an idea is clearer as a picture
- `skills/md-log/`: `/md-log notes.md` links a markdown file as the lesson log (read it in Obsidian); `/md-log off` stops it
- `hooks/md_log.py`: the log writer. Hooks add your prompts and each quiz question and answer; Claude adds the lesson text itself, so the terminal stays short
- `agents/`: `researcher`, `svg-maker`, `mermaid-maker`, the subagents the system delegates to
- `settings.json`: the hook wiring, plus permissions for web research and diagram rendering

Quizzes and questions go through Claude Code's built-in `AskUserQuestion` popup, and Claude grades each answer itself (✓/✗, correct answer, explanation). To say you don't know, pick **Other** and type `idk`.

## Install

This repo **is** a `.claude` directory. From your learning project's root (ideally an Obsidian vault):

```bash
git clone https://github.com/danielskuczi/learn .claude
touch notes.md
claude
```

Then in Claude Code: `/md-log notes.md` (optional) and ask it to teach you something.

## Requirements

- Claude Code
- `python3` (for the md-log hook)
- `node`/`npx` (the diagram makers fetch `@mermaid-js/mermaid-cli` and `@resvg/resvg-js-cli` on first use; mermaid-cli downloads a headless Chromium once)

## Notes

- Diagrams are saved to `viz/` in the project root and embedded as `![[viz-....png|500]]`, which Obsidian renders.
- The terminal is for talking and answering; the log is for reading. Lessons, grading and diagrams only appear in the log, and each quiz question shows up there before you answer it.
- The teaching skill is written for one learner. Edit `skills/teach/SKILL.md` to fit how you learn best.
