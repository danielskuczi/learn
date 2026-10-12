"""Run: python3 hooks/test_md_log.py"""
import os
import tempfile

import md_log

d = tempfile.mkdtemp()
md_log.STATE = os.path.join(d, "state.json")
path = os.path.join(d, "log.md")
open(path, "w").close()
assert not md_log.log({"hook_event_name": "say", "text": "x"})  # not linked yet
md_log.save_state({"file": path, "last": None})

q = {"questions": [{"header": "Quiz", "question": "What is $\\dot x$?", "options": [{"label": "-6e^{-2t}"}, {"label": "packets"}]}]}
for e in [
    {"hook_event_name": "UserPromptSubmit", "prompt": "teach me week 1"},
    {"hook_event_name": "UserPromptSubmit", "prompt": "/md-log notes.md"},
    {"hook_event_name": "say", "text": "First, derivatives."},
    {"hook_event_name": "say", "text": "Second part."},
    {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {}},
    {"hook_event_name": "PreToolUse", "tool_name": "AskUserQuestion", "tool_input": q},
    {"hook_event_name": "PostToolUse", "tool_name": "AskUserQuestion",
     "tool_response": {**q, "answers": {"What is $\\dot x$?": "-6e^{-2t}"}, "annotations": {"What is $\\dot x$?": {"notes": "guessed"}}}},
    {"hook_event_name": "say", "text": "✓ Correct."},
]:
    md_log.log(e)

out = open(path).read()
assert "> [!quote] YOU\n\nteach me week 1" in out and "/md-log" not in out
assert out.count("[!abstract] CLAUDE") == 2  # consecutive says share a header; the one after the answer gets a new one
assert out.index("Second part.") < out.index("What is") < out.index("Your answer: $-6e^{-2t}$") < out.index("✓ Correct.")
assert "> 1. $-6e^{-2t}$" in out and "> 2. packets" in out and "Note: guessed" in out
assert md_log.mathify("the solution x^2 grows forever") == "the solution x^2 grows forever"
print("ok")
