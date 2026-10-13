# Handoff Prompts — linking claude.ai Project ↔ Claude Code

## Workflow
1. **Plan and learn concepts** in the claude.ai Project.
2. Type **"handoff"** and paste the output into `docs/DECISIONS.md`. Update "Current status" in `CLAUDE.md`.
3. **Write the code yourself** in VS Code with Claude Code as tutor (it reads `CLAUDE.md` automatically).
4. End each coding session with the session-end prompt. Paste that summary into the Project when you need planning help.

Rule of thumb: **Project = what and why. Claude Code = how, in your own code.**

---

## A. claude.ai Project

### Start a milestone
```
I'm starting [M#: name]. Before I code:
1. Ask me what I already know about this, then fill the gaps.
2. Break the milestone into small ordered steps with a "done when" for each.
3. List the 1–2 design choices I need to make. Give me hints, not answers.
```

### Think through a design choice
```
I need to decide [e.g. how to represent a swipe as model input].
My current idea is [your idea]. Poke holes in it with questions or hints
first. If I'm still stuck, give the trade-offs and your recommendation.
```

### Check my understanding
```
Quiz me with 3 short questions on [concept, e.g. landmark normalisation /
what a training loop does each step / precision vs recall per class].
One at a time; wait for my answer, then tell me directly if I'm wrong.
```

### Handoff
```
handoff
```

### Review progress
```
Session summary from Claude Code: [paste].
Am I on track? What should next session focus on? Flag overscoping or
gaps in my understanding.
```

---

## B. Claude Code (VS Code)

### Start of session
```
Read CLAUDE.md and docs/DECISIONS.md. Tell me where I am in 3 lines and
the next small step with its "done when". Don't write code.
```

### Before implementing something
```
I'm about to implement [feature] in [file]. Ask me how I'd approach it
first. Then give hints on the APIs or logic I need. Don't write the code.
```

### Stuck
```
I'm stuck on [problem]. Here's what I tried: [...]. Give me a hint only.
```
Then if needed: `Bigger hint.` Then if needed: `Show me and explain each line.`

### Explain code (yours or a library's)
```
Explain [file / function / snippet] line by line, then ask me 2 questions
to check I understood it.
```

### Code review
```
Review [file] as a senior CV engineer would. List issues in priority order
with why each matters. Suggest small diffs, but don't apply them.
```

### Debugging
```
[Error / behaviour.] Help me list hypotheses for the cause and how to test
each one. Don't give the fix yet.
```

### Practice rep
```
Give me a small exercise to practise what I just did (e.g. write the eval
loop again from memory, or extend it to a new gesture). Then review my attempt.
```

### Allow code (boilerplate only, e.g. argparse, plotting)
```
Write it: [small specific task]. Then walk me through it and ask me one
question about it.
```

### End of session
```
Summarise this session for docs/devlog.md in under 8 lines: what I did,
what worked, what failed and why, what I learned, next step. Then update
"Current status" in CLAUDE.md. Show me the changes before applying them.
```

---

## C. Reusing for later projects
For **sign language to text** or **bouldering pose analysis**: copy `CLAUDE.md`, replace Project / Tech stack / Milestones / Design questions, and keep "About me" and "How to work with me" unchanged. Add the new project to the roadmap in the Project instructions.
