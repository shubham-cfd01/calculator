# CI/CD with GitHub Actions

How to make GitHub run your checks automatically, and how a workflow file is
actually put together - using this calculator repo.

Read [WORKFLOW.md](WORKFLOW.md) first if you have not; this doc assumes you
know the issue/branch/PR/merge loop.

---

## 1. What CI and CD mean

| Term | Full name | What it means in practice |
| --- | --- | --- |
| **CI** | Continuous Integration | Every push runs your checks automatically. Broken code gets caught in minutes, not weeks. |
| **CD** | Continuous Delivery/Deployment | Once checks pass, the code ships somewhere automatically - a server, a registry, an app store. |

CI is the part you will use every day. CD only matters once you have somewhere
to deploy to.

**The honest version:** CI is a robot running the terminal commands you would
have run yourself, on a clean machine, every single time, without forgetting.
That is the whole idea. It is not intelligent - see the note at the end of
section 4.

---

## 2. Where workflows live

```
.github/workflows/ci.yml
```

That path is mandatory - GitHub only looks in `.github/workflows/`. The file
name is yours to choose (`ci.yml`, `test.yml`, `deploy.yml`). One file per
workflow; you can have many.

The file must be committed and pushed. GitHub reads it from the repo, not from
your disk, so nothing runs until you push.

---

## 3. Anatomy of a workflow file

Here is a complete CI workflow for this project. Every line is explained below.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Get the code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Check it compiles
        run: python -m py_compile app.py

      - name: Run tests
        run: pytest -v
```

### Line by line

| Key | What it does |
| --- | --- |
| `name` | Label shown in the Actions tab. Cosmetic only. |
| `on` | **The trigger.** Which events start this workflow. |
| `jobs` | One or more units of work. Each gets its own fresh machine. |
| `test` | Your name for the job. Arbitrary, shows in the UI. |
| `runs-on` | Which OS. `ubuntu-latest` is fastest and cheapest - use it unless you need Windows or macOS. |
| `steps` | The commands, run top to bottom. First failure stops the job. |
| `uses` | Runs a **prebuilt action** written by someone else. |
| `run` | Runs a **shell command**, exactly as you would type it. |
| `with` | Arguments passed to a `uses` action. |
| `name` (in a step) | Optional label for that step in the log. Worth adding - it makes failures readable. |

### `uses` vs `run` - the key distinction

```yaml
- uses: actions/checkout@v4        # someone else's reusable action
- run: pip install -r requirements.txt   # your own shell command
```

`uses` pulls in a packaged action from GitHub Marketplace. The `@v4` pins the
version - always pin it, or a future update can silently break your workflow.

Two actions you will use in almost every Python workflow:

- `actions/checkout@v4` - clones your repo onto the runner. **Without this the
  machine is empty.** Nearly every workflow starts with it.
- `actions/setup-python@v5` - installs a specific Python version.

Everything else is usually just `run`.

### The runner is a fresh, empty machine

This is the single most useful mental model. Every job gets a brand-new Ubuntu
VM with nothing on it - no code, no `.venv`, no packages. That is why you must
check out the code and install dependencies explicitly.

It is also why CI catches the "works on my machine" bug: your `.venv` has
packages you installed by hand months ago. The runner has *only* what
`requirements.txt` lists. Forget one, and CI goes red immediately.

The machine is destroyed when the job ends. Nothing persists between runs.

---

## 4. Triggers - the `on` block

```yaml
on:
  push:
    branches: [main]        # only pushes to main
  pull_request:             # every PR, any branch
  workflow_dispatch:        # a manual "Run workflow" button in the UI
  schedule:
    - cron: "0 6 * * *"     # every day at 06:00 UTC
```

| Trigger | Use it for |
| --- | --- |
| `pull_request` | **The important one.** Puts a green check or red X on the PR before you merge. |
| `push` | Verifying `main` stays healthy after merges. |
| `workflow_dispatch` | Deploys and one-off jobs you want to trigger by hand. |
| `schedule` | Nightly builds, dependency checks. Uses UTC, and cannot be faster than every 5 minutes. |

Most repos want `pull_request` plus `push` to `main` - which is what the
workflow in section 3 does.

### What "passing" actually means

A step passes if its command exits with code `0`. That is the entire test.
GitHub does not read your code or judge it - it runs your commands and reports
exit codes.

So a workflow only catches what you explicitly tell it to check. A workflow
whose only step is `echo hello` passes forever, on completely broken code.

---

## 5. Adding real tests

`py_compile` only catches syntax errors. To catch logic bugs you need tests.
Move the calculation out of the UI code so it can be tested:

```python
# calculator.py
def calculate(a, b, op):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "^":
        return a ** b
    if b == 0:
        return None
    return a / b
```

```python
# test_calculator.py
from calculator import calculate

def test_add():
    assert calculate(2, 3, "+") == 5

def test_power():
    assert calculate(2, 10, "^") == 1024

def test_power_of_zero():
    assert calculate(2, 0, "^") == 1        # must not hit the divide-by-zero branch

def test_divide_by_zero():
    assert calculate(5, 0, "/") is None
```

Add `pytest` to `requirements.txt`, and the `pytest -v` step already in the
workflow starts doing real work.

**This is where CI earns its keep.** `test_power_of_zero` is exactly the bug
that appears if the `^` branch is placed below `elif b == 0` in `app.py`. The
file still compiles, so `py_compile` sees nothing wrong - only a real test
catches it.

---

## 6. Useful additions

### Cache pip downloads (faster runs)

```yaml
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
```

One line, and repeat runs skip re-downloading packages.

### Test several Python versions at once

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pytest
```

A **matrix** runs the same job once per value, in parallel. Three versions,
three machines, same wall-clock time.

### Secrets

Never put a password or API key in the YAML - the repo is readable. Store it in
repo Settings, Secrets and variables, Actions, then reference it:

```yaml
      - run: ./deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}
```

Secrets are masked in logs. `${{ }}` is workflow expression syntax, evaluated
by GitHub before the step runs.

---

## 7. The CD half

CD means "after checks pass, ship it". A deploy job that waits for tests:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest

  deploy:
    needs: test                                    # waits for test to pass
    if: github.ref == 'refs/heads/main'            # only on main, never on PRs
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "deploy step goes here"
```

Two keys do the work:

- `needs: test` - creates the dependency. If `test` fails, `deploy` never runs.
- `if:` - a condition. Without it, deploy would fire on pull requests too.

Jobs run in **parallel** by default; `needs` is what forces an order.

**For this Streamlit app specifically:** you probably do not need a CD job.
[Streamlit Community Cloud](https://share.streamlit.io) connects directly to
your GitHub repo and redeploys itself on every push to `main` - no workflow
required. CD through Actions matters when you are pushing a Docker image,
publishing to PyPI, or deploying to your own server.

---

## 8. Reading failures

In the browser: **Actions** tab, click the run, click the red step. The log
shows the exact command and its output.

From the terminal:

```powershell
gh run list                   # recent runs and their status
gh run view                   # detail of the latest run
gh run view --log-failed      # just the steps that failed
gh run watch                  # live-follow a run in progress
gh workflow list              # workflows defined in the repo
gh run rerun                  # re-run the last one
```

Common first-time failures:

| Error | Cause |
| --- | --- |
| `No such file or directory: app.py` | Missing `actions/checkout@v4` - the runner is empty |
| `ModuleNotFoundError` | Package is in your `.venv` but not in `requirements.txt` |
| `pytest: command not found` | `pytest` not listed in `requirements.txt` |
| Workflow does not run at all | File is not in `.github/workflows/`, not pushed, or the `on:` trigger does not match |
| `Invalid workflow file` | YAML indentation. Use 2 spaces, never tabs. |

---

## 9. Cheat sheet

```powershell
# Watch and debug
gh run list
gh run view --log-failed
gh run watch

# On a PR
gh pr checks                  # status of checks for the current branch
```

```yaml
# The minimum useful workflow
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: pip install -r requirements.txt
      - run: pytest
```

The rules worth memorising:

1. The file goes in `.github/workflows/` and must be pushed to exist.
2. Every job starts on an empty machine - check out, then install.
3. `uses` = someone else's action, `run` = your shell command.
4. Exit code 0 means pass. That is the only definition.
5. CI catches only what you tell it to check.
