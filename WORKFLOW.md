# The GitHub Workflow

How to raise an issue, fix it on a branch, open a pull request, review it, and
merge it - using this calculator repo as the example.

Every command here works as-is. `gh` is already installed and logged in as
`shubham-cfd01`.

---

## 1. The mental model

The loop everyone uses, in five steps:

```
  ISSUE          BRANCH          COMMITS         PULL REQUEST      MERGE
"power op   ->  feature/    ->  write the   ->  "please review  ->  code joins
 missing"       power-op        code            my change"          main
    #1                                            #2                  |
    ^                                                                 |
    +------------------ issue auto-closes ---------------------------+
```

Why not just edit `main` directly? Because a branch lets you write broken code
safely, a PR gives a place to review it before it becomes real, and the issue
records *why* the change happened. Six months later the PR is the only thing
that explains your own code to you.

### The five words

| Word | What it actually is |
| --- | --- |
| **Issue** | A numbered to-do item. A bug report or a feature request. No code. |
| **Branch** | Your own copy of the code. Changes here don't affect `main`. |
| **Commit** | A saved checkpoint with a message explaining the change. |
| **Pull request (PR)** | A request to merge your branch into `main`, plus review and discussion. |
| **Merge** | Accepting the PR. Your code becomes part of `main`. |

Issues and PRs share one numbering pool. If your issue is `#1`, your PR is `#2`.

---

## 2. Walkthrough: the running example

Our calculator supports `+ - * /`. Let's add a power operation, the full way.

### Step 1 - Raise the issue

An issue is a written description of what's wrong or missing. Write it before
you write code; it forces you to define "done".

```powershell
gh issue create --title "Add power operation" --body "The calculator supports + - * / but not exponentiation. Add a ^ option that computes a ** b."
```

It prints a URL ending in `/issues/1`. That `1` is your issue number.

Useful issue commands:

```powershell
gh issue list
gh issue view 1
gh issue view 1 --web
gh issue close 1
gh issue comment 1 --body "starting on this"
```

**In the browser instead:** repo page, **Issues** tab, **New issue**.

**What makes a good issue:** what you expected, what happened instead, and how
to reproduce it. For a bug, paste the actual error text.

### Step 2 - Create a branch

Never work on `main`. Start from an up-to-date `main` every time:

```powershell
git checkout main
git pull
git checkout -b feature/power-operation
```

`checkout -b` creates the branch *and* switches to it. Confirm with
`git branch --show-current`.

Naming is convention, not rule. Common: `feature/...`, `fix/...`, `docs/...`.
Some people use `1-add-power-operation` to embed the issue number.

### Step 3 - Fix it

Edit `app.py`. Add `"^"` to the operation list and handle it:

```python
op = st.selectbox("Operation", ["+", "-", "*", "/", "^"])
```

```python
    elif op == "^":
        result = a ** b
```

Test it locally before committing - a PR that was never run wastes a
reviewer's time:

```powershell
streamlit run app.py
```

Then commit:

```powershell
git add app.py
git commit -m "Add power operation to calculator"
```

Commit messages: imperative mood ("Add", not "Added"), and say *why* if it
isn't obvious. Several small commits are fine and often better than one large
one.

### Step 4 - Push and raise the PR

The first push sends the branch to GitHub:

```powershell
git push -u origin feature/power-operation
```

`-u` links the local branch to the remote one, so later pushes are just
`git push`.

Now open the PR:

```powershell
gh pr create --title "Add power operation" --body "Adds a ^ option to the calculator. Closes #1"
```

**The `Closes #1` line is the important part.** It links the PR to the issue,
and when the PR merges, GitHub closes issue #1 automatically. Also works:
`Fixes #1`, `Resolves #1`.

Shortcut that fills title and body from your commits:

```powershell
gh pr create --fill
```

**In the browser instead:** after pushing, GitHub shows a "Compare and pull
request" banner. Click it.

### Step 5 - Review the PR

This is the actual point of the whole exercise: a checkpoint before code
becomes permanent.

```powershell
gh pr list
gh pr view 2
gh pr diff 2
gh pr checks 2
gh pr view 2 --web
```

Read `gh pr diff 2` as if someone else wrote it. Does it do what the issue
asked? Anything broken? Anything left in by accident - debug prints, secrets,
commented-out code?

Leaving review feedback:

```powershell
gh pr comment 2 --body "Looks good, but ^ with a huge exponent may hang."
gh pr review 2 --approve
gh pr review 2 --request-changes --body "Please guard against 0 ** -1"
```

If changes are requested, just commit and push to the same branch - the PR
updates itself. **A PR tracks the branch, not a snapshot.** Nothing needs to be
closed and reopened.

```powershell
git add app.py
git commit -m "Guard against negative exponent of zero"
git push
```

> **Solo repo note:** GitHub blocks you from formally approving your own PR.
> You can still merge it - approval is only *required* if branch protection
> says so. Review your own diff anyway; it catches real mistakes.

### Step 6 - Accept (merge) the PR

```powershell
gh pr merge 2 --squash --delete-branch
```

Three merge styles - pick one and stay consistent:

| Flag | What it does | When to use |
| --- | --- | --- |
| `--squash` | All commits become one clean commit on `main` | **Default choice.** Tidy history. |
| `--merge` | Keeps every commit plus a merge commit | When individual commits matter |
| `--rebase` | Replays commits onto main, no merge commit | Linear history, no extra commit |

`--delete-branch` cleans up the branch both remotely and locally. The branch
has served its purpose once merged.

When this runs: PR #2 closes, **issue #1 closes automatically** because of the
`Closes #1`, and `main` now has your code.

### Step 7 - Return to main

Your local `main` is still behind, because the merge happened on GitHub:

```powershell
git checkout main
git pull
```

Now you are synced and ready for the next issue. That is the whole loop.

---

## 3. How GitHub Actions fits in

Add `on: pull_request` to a workflow and it runs on every PR automatically,
posting a green check or a red X on the PR page:

```yaml
on:
  push:
    branches: [main]
  pull_request:
```

This is why the workflow matters: it tests the code *before* you merge, not
after. Check results with `gh pr checks 2`, or read failures with:

```powershell
gh run list
gh run view --log-failed
```

Repos often require checks to pass before the merge button unlocks. That is
branch protection, configured in repo Settings, Branches.

---

## 4. When things go wrong

| Problem | Fix |
| --- | --- |
| Committed on `main` by mistake | `git branch feature/x` then `git reset --hard origin/main` - moves the work to a branch, resets main |
| Pushed the wrong branch name | `git push origin --delete old-name` then push again |
| PR shows unrelated files | Your branch is stale: `git checkout main; git pull; git checkout your-branch; git merge main` |
| Merge conflict | Git marks the file with `<<<<<<<` and `>>>>>>>`. Edit to keep what you want, delete the markers, then `git add` and `git commit` |
| Want to abandon a PR | `gh pr close 2` |
| Forgot `Closes #1` | Comment `Closes #1` on the PR, or close the issue by hand |

---

## 5. Ask Claude for any of this

Plain English works - no need to memorise the commands:

```
create an issue for adding a power operation
make a branch and implement issue #1
open a PR for this branch that closes issue #1
show me the diff of PR #2 and review it
why did the workflow on my PR fail?
merge PR #2 and clean up the branch
I committed to main by accident, fix it
```

Claude confirms before pushing, merging, or deleting anything.

---

## 6. Cheat sheet

```powershell
# Issue
gh issue create --title "..." --body "..."
gh issue list
gh issue view 1

# Branch
git checkout main; git pull
git checkout -b feature/name
git branch --show-current

# Commit
git add .
git commit -m "message"
git push -u origin feature/name

# Pull request
gh pr create --fill
gh pr list
gh pr diff 2
gh pr checks 2
gh pr comment 2 --body "..."

# Merge
gh pr merge 2 --squash --delete-branch
git checkout main; git pull
```

The whole loop, one word per step:

```
issue -> branch -> edit -> commit -> push -> PR -> review -> merge -> pull
```
