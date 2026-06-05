---
description: Create a spec markdown file for the next Spendly feature implementation step
arguments:
  - name: step_and_feature
    description: "The step number followed by the feature name (e.g., '2 registration' or '11 login and logout')"
    required: true
---

# Task: Create a Feature Specification Document

## Step 1: Parse and Standardize Arguments
Extract and format the values from the input string:
1. **`step_number`**: Format as a zero-padded, two-digit string (e.g., `2` becomes `02`, `11` remains `11`).
2. **`feature_title`**: Convert into human-readable **Title Case** (e.g., `login and logout` becomes `Login and Logout`).
3. **`feature_slug`**: Convert into a web-safe, lowercase **kebab-case** string. 
   * Strict regex: Allow only `a-z`, `0-9`, and `-`.
   * Truncate to a maximum of 40 characters.
   * Example: `login-and-logout`.

*If the input string cannot be successfully parsed into these three components, halt execution and ask the user for immediate clarification.*

## Step 2: Codebase Context Discovery & Validation
Before generating the specification file, read and inspect the following files to prevent architectural regressions:
* `CLAUDE.md` — To inspect the project roadmap, design conventions, and schema state.
* `app.py` — To evaluate existing routes and application structure.
* `database/db.py` — To evaluate the active database schema definitions and connection handlers.
* `.claude/specs/` — Inspect all files inside this directory to ensure the feature specification does not duplicate a step that has already been scoped out.

**Roadmap Validation Rule:** Cross-reference your parsed `step_number` against the roadmap status inside `CLAUDE.md`. If the requested step is already marked complete or fully implemented, warn the user explicitly and stop execution.

## Step 3: Write the Specification Document
Generate a new specification file and save it exactly to the path: 
`.claude/specs/<step_number>-<feature_slug>.md`

The contents of the markdown file must strictly follow this structural blueprint:

```markdown
# Spec: <feature_title>

## Overview
[Provide a concise, single-paragraph explanation describing exactly what this feature does, how it functions, and why it is positioned at this specific stage of the Spendly roadmap.]

## Depends On
[List the previous developmental steps or backend components this feature relies upon before it can be safely built.]

## Routes
[List every new HTTP route required using the following template format:]
* **METHOD /path** — Description of purpose — Access Level (`public` / `logged-in`)

*If no new endpoints are required, explicitly print: "No new routes."*

## Database Changes
[Detail any new database tables, structural columns, indexes, or foreign key constraints needed for this feature. Cross-examine this data against `database/db.py` to prevent naming collisions.]

*If no structural data changes are required, explicitly print: "No database changes."*

## Templates
* **Create:** [List the exact workspace paths for any brand new HTML templates to be added.]
* **Modify:** [List the workspace paths for any pre-existing templates that must be altered, detailing the intended modifications.]

## Files to Change
[Provide a definitive bulleted list of every existing code file in the repository that will need code modifications to realize this feature.]

## Files to Create
[Provide a clear bulleted list of every brand new code, script, style, or asset file that needs to be generated from scratch.]

## New Dependencies
[Specify any brand new Python pip packages required for this feature. If no new packages need to be installed, explicitly state: "No new dependencies".]

## Rules for Implementation
[Specific behavioral constraints and code architectures Claude must strictly follow during development. Always include the following baseline directives:]
1. **No SQLAlchemy or ORMs:** Interact with databases using light, direct connections.
2. **Parameterized Queries Only:** Never build raw SQL queries using python string concatenation or dynamic formatting.
3. **Password Security:** All passwords must be securely processed and hashed using `werkzeug.security`.
4. **Design/CSS Variables:** Utilize existing custom CSS design tokens and layout variables; never hardcode custom hex color codes.
5. **Template Inheritance:** Ensure every newly made HTML view layout strictly extends from `base.html`.

## Definition of Done
[Provide a highly targetable, testable checklist. Each item must represent a verifiable user action or application response that can be directly confirmed by executing the application locally.]
\```