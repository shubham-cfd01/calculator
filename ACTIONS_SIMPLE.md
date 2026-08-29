# GitHub Actions, explained once

One example. It works on this repo today. Read this top to bottom and it will
click.

---

## 1. The problem it solves

Right now, to check your calculator is not broken, you type this yourself:

```powershell
python -m py_compile app.py
```

That works. But it only happens **on your machine**, and only **when you
remember**. Forget once, push broken code, and nobody finds out until someone
opens the app.

## 2. What GitHub Actions actually is

**GitHub rents you a computer, and runs your commands on it, automatically.**

That is it. There is no magic and no intelligence. You write down the commands
you would have typed. GitHub types them for you, on a fresh Ubuntu machine, every
time you push.

The YAML file is just you answering three questions:

- **WHEN** should it run?
- **WHERE** should it run?
- **WHAT** commands should it run?

---

## 3. The example

Put this in `.github/workflows/ci.yaml`. Nothing else needed - it works with the
files you already have.

```yaml
name: CI

on: push

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - run: pip install -r requirements.txt

      - run: python -m py_compile app.py
```

Twelve lines. That is a complete, working CI setup.

### Now read it as the three questions

```yaml
name: CI                      # a label. Cosmetic.

on: push                      # WHEN:  every time I push. That is the trigger.

jobs:
  check:                      # a name I made up for this unit of work
    runs-on: ubuntu-latest    # WHERE: a fresh Ubuntu computer

    steps:                    # WHAT:  these four things, in order, top to bottom
      - uses: actions/checkout@v4        # 1. copy my repo onto that computer
      - uses: actions/setup-python@v5    # 2. install Python 3.11
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt   # 3. install streamlit
      - run: python -m py_compile app.py       # 4. check app.py is valid Python
```

### The only two step types

```yaml
- uses: ...    # run a ready-made tool someone else wrote
- run:  ...    # run a shell command, exactly as you would type it
```

`run:` lines are just terminal commands. `pip install -r requirements.txt` is
the same thing you typed in PowerShell. Nothing was translated.

`uses:` lines pull in prewritten tools. You only need two of them here:

- `actions/checkout@v4` - copies your code onto the machine
- `actions/setup-python@v5` - installs Python

### Why steps 1 and 2 exist at all

**The rented computer starts completely empty.** No code, no Python, no
streamlit, no `.venv`. Nothing.

So before you can run anything, you must put your code on it (`checkout`) and
install Python (`setup-python`). That is all those two lines do. Skip
`checkout` and step 4 fails with `app.py: No such file or directory`, because
the machine genuinely does not have your file.

The computer is deleted when the job finishes. Next push gets a brand new one.

---

## 4. What happens when you push

You run:

```powershell
git add .
git commit -m "add workflow"
git push
```

Then, without you doing anything else:

```
  1. GitHub sees the push
  2. Reads .github/workflows/ci.yaml
  3. Sees "on: push" matches -> starts the workflow
  4. Boots a fresh Ubuntu computer
  5. Runs your 4 steps in order:
        copy repo        -> ok
        install Python   -> ok
        pip install      -> ok
        py_compile       -> ok
  6. All steps succeeded -> green tick
  7. Deletes the computer
```

Takes about 30 seconds.

### Where to watch it

Open your repo on GitHub, click the **Actions** tab. Your run is listed there.
Click it, click the `check` job, and you see every step with its real terminal
output - the same text you would have seen locally.

Or from PowerShell:

```powershell
gh run watch          # follow it live
gh run list           # recent runs, pass or fail
gh run view --log     # full output
```

### How pass and fail are decided

Every command returns a number when it finishes. `0` means it worked.

```
python -m py_compile app.py   ->  exits 0  ->  step passes  ->  green
python -m py_compile app.py   ->  exits 1  ->  step fails   ->  red, job stops
```

That is the entire rule. GitHub does not read or understand your code. It runs
the commands you listed and looks at the numbers they return.

---

## 5. Prove it to yourself

This is the bit that makes it real. Break the file on purpose:

```powershell
# add a deliberate syntax error
echo "def broken(" >> app.py
git add app.py
git commit -m "break it on purpose"
git push
gh run watch
```

Within a minute the run goes **red**. Open it and you will see `py_compile`
reporting a `SyntaxError` - caught by GitHub, not by you.

Now undo it:

```powershell
git checkout app.py     # only if not committed
# or, since you did commit:
git revert HEAD --no-edit
git push
gh run watch
```

**Green.** You have now seen the entire point of CI: a machine that checks your
work every single time, whether or not you remember to.

---

## 6. One warning about your current file

The workflow you pasted ends with:

```yaml
      - name: Run tests
        run: pytest -v
```

**That step will fail.** Two reasons: `pytest` is not in `requirements.txt`, so
it is not installed, and there are no test files in this repo. The run will go
red on a problem with the workflow, not with your code - which is confusing
while you are still learning.

Delete that step for now. Use the 12-line version in section 3. Add tests later,
once green runs feel normal.

---

## 7. What to add later

Once this makes sense, these are the natural next steps - one at a time:

| Add this | To get |
| --- | --- |
| `on: [push, pull_request]` | A green check on your PRs before you merge |
| A `test_calculator.py` + `pytest` step | Catches logic bugs, not just syntax errors |
| `cache: "pip"` under setup-python | Faster runs |

But get one green tick first. Everything else is a variation on the same
twelve lines.

---

## The whole idea in four lines

1. A workflow is a list of terminal commands.
2. GitHub runs them on a fresh, empty computer when the trigger fires.
3. That is why you check out the code and install Python first.
4. Exit code 0 means pass. Nothing else is being judged.
