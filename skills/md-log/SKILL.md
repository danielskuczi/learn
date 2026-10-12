---
name: md-log
description: Link a markdown file as the lesson log (read it in Obsidian; lessons go there instead of chat). Usage /md-log <file.md> to link, /md-log off to stop.
disable-model-invocation: true
argument-hint: <file.md> | off
---

Run exactly one Bash command, then report its output in one line:

- If the argument is `off`: `python3 .claude/hooks/md_log.py unlink`
- Otherwise: `python3 .claude/hooks/md_log.py link "$ARGUMENTS"`
