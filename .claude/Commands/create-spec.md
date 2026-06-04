---
description: Run Git health checks, create an isolated feature branch, and generate an implementation specification file
arguments:
  - name: step_and_feature
    description: "The step number followed by the feature name (e.g., '3 expense tracking' or '11 login and logout')"
    required: true
---

# Task: Git Feature Branch Creation and Specification Generation

## Step 1: Check Working Directory Integrity
Run `git status` using the terminal tools to evaluate the active repository state. Check thoroughly for any uncommitted changes, unstaged modifications, or untracked files.
* **Strict Guardrail:** If the working directory contains any uncommitted changes, halt execution immediately. Warn the user to commit, reset, or stash their changes before attempting to spin up a new feature step. Do not modify any files or execute further steps until `git status` reports a completely clean working directory.

## Step 2: Parse and Standardize Arguments
Extract and format the values from the input arguments configuration:
1. **`step_number`**: Format as a zero-padded, two-digit string (e.g., `3` becomes `03`, `11` remains `11`).
2. **`feature_title`**: Convert into human-readable **Title Case** (e.g., `expense tracking` becomes `Expense Tracking`).
3. **`feature_slug`**: Convert into a web-safe, lowercase **kebab-case** string.
   * Strict regex: Allow only `a-z`, `0-9`, and `-`.
   * Truncate to a maximum of 40 characters (e.g., `expense-tracking`).
4. **`branch_name`**: Format precisely as `feature/<feature_slug>` (e.g., `feature/expense-tracking`).

*If the input string cannot be successfully parsed into these components, halt execution and ask the user for immediate clarification.*

## Step 3: Validate Branch Availability
Run `git branch -a` to inspect all local and remote branches. If the target `branch_name` is already taken, safely append an incremental numeric suffix to keep it unique (e.g., `feature/expense-tracking-01`, `feature/expense-tracking-02`).

## Step 4: Synchronize Main Branch
Switch to main and pull upstream changes to ensure the branching baseline is up to date:
```bash
git checkout main
git pull origin main
```

## Step 5: Create and Switch to Feature Branch
```bash
git checkout -b <branch_name>
```
Confirm the active branch with `git branch` and report it to the user before continuing.

## Step 6: Write the Specification File
Create the spec file at `.claude/Specs/<step_number>-<feature_slug>.md` using the format below. Ask the user clarifying questions about the feature before writing — do not invent requirements.

Use this format:

# Feature: <feature_title>

## Overview
<brief description of the feature>

## User Stories
<list of user stories>

## Functional Requirements
<list of functional requirements>

## Non-Functional Requirements
<list of non-functional requirements>

## Implementation Details
<detailed implementation details including files to change, pseudocode, and dependencies>

## Acceptance Criteria
<checklist of acceptance criteria>

---

Once the spec is complete, confirm the branch name and spec file path to the user.
