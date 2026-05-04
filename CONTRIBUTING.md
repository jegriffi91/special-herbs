# Contributing to Special Herbs

> Conventions for substrate-side development. Read [AGENTS.md](AGENTS.md) and [CLAUDE.md](CLAUDE.md) first — those are mandatory; this file is the operational how-to.

## Branching and worktrees

- `main` is protected. No direct pushes; merges land via PR only.
- Develop in worktrees, not branches in the main checkout. Mirrors KG's convention.

```bash
# From the repo root
git worktree add .claude/worktrees/<feature-name> -b <branch-name>
cd .claude/worktrees/<feature-name>
```

The `.claude/worktrees/` directory is gitignored; each worktree is throwaway. When the PR squash-merges, delete the worktree:

```bash
git worktree remove .claude/worktrees/<feature-name>
git branch -D <branch-name>
```

## Local environment

```bash
make setup
```

This creates `.venv/`, installs dev dependencies (`requirements-dev.txt`), installs the package in editable mode, and registers pre-commit hooks. Use `source .venv/bin/activate` before running ad-hoc Python.

## Pre-merge gates

Every PR runs the [`ci.yml`](.github/workflows/ci.yml) workflow on the self-hosted `[self-hosted, special-herbs]` runner. The gate requires:

1. Branch up to date with `origin/main` (rebase, don't merge-commit).
2. `ruff check` + `ruff format --check` pass.
3. `lint-imports` passes (subsystem-boundary contracts in `pyproject.toml` `[tool.importlinter]`).
4. `bandit -r src/special_herbs` clean (skipped pre-Phase-1 when `src/` has no production code yet).
5. `pytest -m "not live"` passes.
6. Line coverage **≥ 80%** (configured in `pyproject.toml` `[tool.coverage.report] fail_under = 80`).

Run the same gate locally before opening a PR:

```bash
make ci-local
```

### Coverage threshold rationale

80% line coverage is the floor. The reasoning, briefly:

- Library-style modules (`formats/`, `observability/`, `tape/`) are pure functions and naturally hit 90%+. They pull the average up.
- Pipeline modules (`training/`, `eval/`, `release/`, `plv/`, `ingest/`) orchestrate side effects and land in the 70–80% range when tested primarily via tape-replay integration tests rather than exhaustive unit coverage.
- 80% catches dead code and forces test-first discipline on pure-function code, but doesn't punish pipeline scaffolding that lands before exhaustive coverage.
- Stub functions (`signer.sign`, `verification.verify_signature`) raise `NotImplementedError` and are excluded from coverage by the `exclude_lines` rule.

Re-evaluate the threshold once Phase 1 production code stabilizes (likely 85% target then); avoid pushing to 90%+ which would block legitimate orchestration scaffolding PRs.

## Self-hosted runner setup

The CI workflow runs on a GitHub Actions self-hosted runner labelled `[self-hosted, special-herbs]`. The runner lives on the M2 Ultra Mac Studio that also hosts KG's `[self-hosted, kg]` runner — separate labels prevent cross-project job collisions.

Operator-only setup (one-time per machine):

1. Register a self-hosted runner from the GitHub repo settings: **Settings → Actions → Runners → New self-hosted runner**.
2. When prompted for labels, use `special-herbs` (the `self-hosted` label is added automatically).
3. Install as a launchd service so it survives reboots:

```bash
cd ~/actions-runner-special-herbs
./svc.sh install
./svc.sh start
```

The substrate runner and KG runner can share the same Mac Studio — they're separate processes per ADR-0003 §6 (process isolation).

## Branch protection

Configure on the GitHub repo (Settings → Branches → Branch protection rules → `main`):

- Require pull request before merging.
- Require status checks to pass: `CI / ci`.
- Require branches to be up to date before merging.
- Restrict pushes that create matching branches.
- Allow squash merging only.

## Commit conventions

- Subject line: imperative present tense, ≤72 chars. Match recent `git log` style: `docs: …`, `feat(formats): …`, `fix(release): …`, etc.
- Body explains the *why*, not the *what* (the diff shows what changed).
- Use HEREDOC for multi-line messages so newlines render correctly in the GitHub UI.
- Never `--no-verify` to skip pre-commit — fix the underlying issue.

## ADRs

Architectural decisions land as ADRs in [docs/architecture/](docs/architecture/). Use [ADR-template.md](docs/architecture/ADR-template.md) as the starting point. Number sequentially; never reuse a number even for a withdrawn proposal. Foundational ADRs (0001, 0002, 0003) can only be modified by a new ADR that explicitly supersedes them.

## What this repo MUST NOT contain

See [AGENTS.md §"What This Repo MUST NOT Contain"](AGENTS.md). The short version: no trading code, no brokerage APIs, no consumer-side imports, no live-trading strategy YAML.
