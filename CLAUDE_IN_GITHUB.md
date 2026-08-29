# Claude in GitHub

Two ways to put Claude to work on your pull requests, explained against this
calculator repo.

Your setup, checked: repo `shubham-cfd01/calculator`, public, and you have
**admin** on it. No secrets configured yet, one workflow (`ci.yaml`).

---

## 1. The two paths

| | **Code Review** (managed) | **GitHub Action** (DIY) |
| --- | --- | --- |
| What it is | Anthropic-hosted service | A workflow you write yourself |
| You build | Nothing - turn it on | A `.yaml` file |
| What it does | Posts review comments on PRs | Anything: writes code, commits, reports |
| Runs on | Anthropic's infrastructure | GitHub's runners, your API key |
| Cost | Included in team/enterprise plan | Your Anthropic API usage |
| Needs | Org admin, team/enterprise plan | Repo admin, an API key |

**The dividing line:** Code Review *comments*. The Action *acts*.

---

## 2. Which applies to your repo

Read this before you spend time on either.

**Code Review - probably not available to you.** It requires a team or
enterprise plan and an organization admin to enable it from Claude Code admin
settings. `shubham-cfd01/calculator` is a personal repo, not an org repo, so
there is no admin console to switch it on. If you are not on a team plan, skip
to the Action.

**The GitHub Action - available, but it costs money.** It runs on GitHub's
runners and calls the Anthropic API using a key you supply. That is **API
billing, separate from any Claude Code subscription you already pay for**. A
small run on this tiny repo is cents, but a scheduled job left running is a
bill you should watch.

**The free option you already have.** In your terminal, right now:

```powershell
/code-review           # review your current changes
/code-review --fix     # review, then apply the fixes
```

No setup, no API key, no workflow. For a solo project this covers most of what
the managed service would do - the difference is it runs when *you* ask, not
automatically on every PR.

---

## 3. How this differs from your `ci.yaml`

This is the concept to get straight, because both are workflow files in the
same folder.

```
.github/workflows/ci.yaml        runs YOUR COMMANDS
                                 "run py_compile"  -> exit 0 or 1
                                 Deterministic. Same input, same output.
                                 Cannot write code.

.github/workflows/claude.yaml    runs AN AGENT
                                 "fix the bug in this issue" -> reads the repo,
                                 edits files, commits, opens a PR, comments
                                 Non-deterministic. Judgement, not exit codes.
                                 Can write code.
```

Your `ci.yaml` checks that `app.py` compiles. A Claude workflow could *fix*
`app.py` when it does not. Same folder, same trigger system, completely
different kind of step.

---

## 4. Setup (one time)

### Step 1 - install the GitHub app

In Claude Code, in this project:

```
/install-github-app
```

You have admin on the repo, so this will work. It walks you through installing
the Claude GitHub app on `shubham-cfd01/calculator` and setting the API key
secret.

### Step 2 - the API key secret

If you set it by hand instead:

```powershell
gh secret set ANTHROPIC_API_KEY
```

It prompts for the value; paste your key from console.anthropic.com. Verify:

```powershell
gh secret list
```

**Never put the key in the YAML file.** Your repo is public - a committed key
is a stolen key within minutes. Secrets are stored by GitHub and masked in
logs.

---

## 5. Working example: @claude on this repo

Create `.github/workflows/claude.yaml`:

```yaml
name: Claude

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  claude:
    runs-on: ubuntu-latest

    permissions:
      contents: write          # let it commit code
      pull-requests: write     # let it open PRs and comment
      issues: write            # let it comment on issues

    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          trigger_phrase: "@claude"
          claude_args: "--max-turns 5"
```

### Reading it against what you already know

The top half is identical to `ci.yaml` - `on`, `jobs`, `runs-on`, `steps`.
Only three things are new:

| New thing | What it does |
| --- | --- |
| `on: issue_comment` | Trigger is **someone commenting**, not a push |
| `permissions:` | What the job is allowed to change in your repo. Without `contents: write` it can read but never commit. |
| `uses: anthropics/claude-code-action@v1` | The agent itself - one prebuilt action, same as `actions/checkout@v4` |

Note there is no `prompt:` here. When the trigger is a comment and you omit
`prompt`, **the comment text becomes the instruction**. That is what makes the
mention style work.

### Actually using it

Commit and push the workflow, then on any issue or PR in your repo, comment:

```
@claude add a square root operation to the calculator
```

What happens:

```
  1. You post the comment
  2. GitHub fires the issue_comment event
  3. Workflow starts, sees "@claude" matches trigger_phrase
  4. Claude reads your repo - app.py, requirements.txt, the docs
  5. Edits app.py, adds the operation
  6. Commits to a branch and opens a PR
  7. Replies to your comment saying what it did
```

Watch it exactly like your CI run:

```powershell
gh run watch
gh run list
```

**Try this first, on your own repo:** open an issue, comment
`@claude add a square root operation`, and read the PR it opens. It is the
same review-and-merge loop from WORKFLOW.md - the only difference is who wrote
the branch.

---

## 6. Working example: a scheduled job

Same action, different trigger. `.github/workflows/weekly.yaml`:

```yaml
name: Weekly summary

on:
  schedule:
    - cron: "0 6 * * 1"      # Mondays 06:00 UTC
  workflow_dispatch:          # plus a manual Run button

jobs:
  summary:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Summarise this week's commits and open an issue with the summary."
          claude_args: "--max-turns 3"
```

Two differences from the mention workflow:

- **`prompt:` is set.** Nobody is typing a comment, so the instruction has to
  live in the file.
- **`contents: read`, not write.** This job only reports. Give a job the
  minimum it needs; a reporting job has no business committing code.

`workflow_dispatch` adds a **Run workflow** button in the Actions tab, so you
can test it without waiting until Monday. Always add it to scheduled
workflows.

---

## 7. Tuning with `claude_args`

`claude_args` is a plain string of CLI flags passed straight to Claude Code -
the same flags the terminal takes.

| Flag | Why |
| --- | --- |
| `--max-turns 5` | **Use always.** Hard cap on the agent loop, so a confused run cannot spin up a bill. |
| `--model claude-sonnet-5` | Cheaper and faster than Opus for routine jobs |
| Permission mode | Nobody is at the keyboard to answer prompts, so an unattended job must not stop and ask |
| Allowed tools | Give the job exactly what it needs. A report job should be read-only. |

The safety story is really two layers, and both matter:

- **`permissions:` in the YAML** - what GitHub *lets* the job touch. The hard
  boundary.
- **`claude_args`** - what the agent is *configured* to do inside that
  boundary.

Set `permissions` to the minimum first. It is the one that GitHub enforces.

---

## 8. The other inputs

| Input | Note |
| --- | --- |
| `anthropic_api_key` | Optional - not needed on Bedrock or Vertex |
| `github_token` | Defaults to `secrets.GITHUB_TOKEN`, which GitHub creates automatically. You rarely set it. |
| `trigger_phrase` | Defaults to `@claude`. Change it if that collides with a real username. |
| `use_bedrock` / `use_vertex` | Route through AWS Bedrock or Google Vertex instead |
| `prompt` | The instruction. Omit on comment triggers to use the comment text. |
| `claude_args` | CLI flags, as above |

---

## 9. What Code Review will not do

If you do get access to the managed service later, know its limits:

- **It never approves or blocks a PR.** It comments; the merge decision stays
  human.
- **No autofix.** It posts findings only. Applying them is a local move:
  `/code-review --fix` in your terminal.
- **Research preview**, team and enterprise plans - expect behaviour to change.

It reviews the diff against your whole codebase rather than the changed lines
alone, then deduplicates and ranks, so you get a few real issues instead of a
wall of nitpicks.

---

## 10. Which to use

```
Just want PR reviews?          -> Code Review if you have it,
                                  otherwise /code-review in your terminal

Want Claude to DO something    -> the GitHub Action
in CI - write code, open PRs,
post reports?
```

**For this repo, today:** use `/code-review` in the terminal - free, instant,
no setup. Add the Action when you actually want something to happen without
you being there, like `@claude` implementing an issue while you are away from
the machine.

Start with the free thing. Add the paid thing when you have a reason.
