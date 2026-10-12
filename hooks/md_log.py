#!/usr/bin/env python3
"""md-log — the lesson log: the terminal is for talking, the linked .md file (read in Obsidian) is for reading.

  md_log.py link <file>   start logging into an existing .md file
  md_log.py unlink        stop logging
  md_log.py say           append stdin (lesson text written by Claude) to the log
  md_log.py               hook mode: reads hook JSON on stdin

Hooks log your prompts (UserPromptSubmit) and each AskUserQuestion
question (PreToolUse) and answer (PostToolUse), straight from the hook payload.
Lesson prose is not mirrored from chat: Claude writes it here with `say`,
so chat stays short.
"""
import json
import os
import re
import sys

# ponytail: one linked log per project folder, not per session
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "md-log.json")


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save_state(state):
    with open(STATE, "w") as f:
        json.dump(state, f, indent=1)


def callout(kind, title, body):
    lines = [f"> [!{kind}] {title}"]
    lines += [f"> {l}" if l else ">" for l in body.split("\n")]
    return "\n".join(lines)


def mathify(label):
    # ponytail: heuristic, wraps bare LaTeX-looking labels ("-6e^{-2t}") in $…$; prose-with-math labels are left as-is
    if "$" not in label and re.search(r"[\\^_{]", label) and not re.search(r"[A-Za-z]{4,} [A-Za-z]{2,}", label):
        return f"${label}$"
    return label


def ask_block(inp):
    out = []
    for q in inp.get("questions", []):
        opts = "\n".join(f"{i}. {mathify(o.get('label', ''))}" for i, o in enumerate(q.get("options", []), 1))
        out.append(callout("question", q.get("header") or "Question", f"{q.get('question', '')}\n\n{opts}"))
    return "\n\n".join(out)


def answer_block(resp):
    answers = resp.get("answers") if isinstance(resp, dict) else None
    if answers:
        body = "\n".join(f"Your answer: {mathify(a)}" for a in answers.values())
        notes = [n.get("notes") for n in (resp.get("annotations") or {}).values() if isinstance(n, dict) and n.get("notes")]
        body += "".join(f"\nNote: {n}" for n in notes)
    else:
        body = str(resp or "(no answer)")
    return callout("info", "Answer", body)


def block_for(event, state):
    """Markdown for one event, or None. Tracks the last speaker so consecutive `say`s share one header."""
    name = event.get("hook_event_name")
    if name == "say":
        text = event["text"].strip()
        block = text if state.get("last") == "claude" else "> [!abstract] CLAUDE\n\n" + text
        who = "claude"
    elif name == "UserPromptSubmit":
        text = (event.get("prompt") or "").strip()
        if not text or text.startswith(("/", "<")):  # slash commands aren't lesson content
            return None
        block, who = "> [!quote] YOU\n\n" + text, "user"
    elif name == "PreToolUse" and event.get("tool_name") == "AskUserQuestion":
        block, who = ask_block(event.get("tool_input") or {}), "question"
    elif name == "PostToolUse" and event.get("tool_name") == "AskUserQuestion":
        block, who = answer_block(event.get("tool_response")), "answer"
    else:
        return None
    state["last"] = who
    return block


def log(event):
    state = load_state()
    if not state or not os.path.exists(state["file"]):
        return False
    block = block_for(event, state)
    if block:
        with open(state["file"], "a") as f:
            f.write("\n\n" + block + "\n")
        save_state(state)
    return True


def main():
    args = sys.argv[1:]
    if args[:1] == ["link"] and len(args) == 2:
        path = os.path.abspath(args[1])
        if not os.path.isfile(path):  # never create files: a typo'd path shouldn't scatter notes
            sys.exit(f"File does not exist: {path}")
        save_state({"file": path, "last": None})
        print(f"Linked {path}.")
    elif args == ["unlink"]:
        if os.path.exists(STATE):
            os.remove(STATE)
        print("Unlinked.")
    elif args == ["say"]:
        if not log({"hook_event_name": "say", "text": sys.stdin.read()}):
            sys.exit("No log linked: put the lesson in chat instead.")
    elif not args:
        log(json.load(sys.stdin))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
