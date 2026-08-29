# Project Guide

A Streamlit calculator used to learn GitHub Actions.

- Repo: https://github.com/shubham-cfd01/calculator
- Branch: `main`
- App: `app.py`

---

## 1. Setup (once)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Run the app (every time)

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

Opens at http://localhost:8501. Press `Ctrl+C` in the terminal to stop.

---

## 3. Git commands you need

| Task | Command |
| --- | --- |
| See what changed | `git status` |
| Stage all changes | `git add .` |
| Stage one file | `git add app.py` |
| Commit | `git commit -m "your message"` |
| Push to GitHub | `git push` |
| Pull latest | `git pull` |
| See history | `git log --oneline` |
| Unstage a file (keep on disk) | `git restore --staged <file>` |
| Undo edits to a file | `git restore <file>` |

Normal daily flow:

```powershell
git add .
git commit -m "what I changed"
git push
```

---

## 4. GitHub Actions basics

A workflow is a YAML file in `.github/workflows/`. GitHub runs it automatically
on the events you list.

Minimal example, `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python -m py_compile app.py
```

The four parts to understand:

- `on` - when it runs (push, pull_request, schedule, workflow_dispatch)
- `jobs` - one or more units of work, run in parallel by default
- `runs-on` - which machine (`ubuntu-latest` is the normal choice)
- `steps` - the actual commands, run top to bottom

To use it: commit the file, push, then open the **Actions** tab on GitHub to
watch it run. A red X means a step failed - click the step to read the log.

Checking runs from the terminal (needs the `gh` CLI):

```powershell
gh run list
gh run view --log
```

---

## 5. Working with Claude Code

Claude edits files, runs commands, and explains errors. Talk to it in plain
English - no special syntax needed.

**Useful things to ask:**

```
add a GitHub Actions workflow that runs on every push
explain why my workflow failed
add a test file for the calculator
run the app and check it works
what does this error mean: <paste error>
commit and push my changes
```

**Slash commands worth knowing:**

| Command | What it does |
| --- | --- |
| `/init` | Creates a `CLAUDE.md` so Claude remembers project context |
| `/code-review` | Reviews your changes for bugs |
| `/clear` | Starts a fresh conversation |
| `/help` | Lists all commands |

**Tips:**

- Paste full error messages - Claude reads them better than a summary.
- Say "keep it simple" if the result is more complex than you wanted.
- Ask "why" after a change if you want to learn, not just get code.
- Claude asks before pushing or deleting things. Read those prompts.

---

## 6. Files in this project

| File | Purpose |
| --- | --- |
| `app.py` | The Streamlit calculator |
| `requirements.txt` | Python packages needed |
| `.gitignore` | Keeps `.venv/` and `__pycache__/` out of git |
| `GUIDE.md` | This file |
