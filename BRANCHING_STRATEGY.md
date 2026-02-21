# Branching Strategy

## Workflow

Basic feature branching off `main`.

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable, working state. All merges go here. |
| `feature/<short-description>` | New functionality or enhancements |
| `bugfix/<short-description>` | Bug fixes |
| `chore/<short-description>` | Refactoring, tooling, docs, tech debt |
| `spike/<short-description>` | Exploratory prototypes / research |

## Rules

1. All work happens on a branch off `main` — no direct commits to `main` after initial project setup.
2. Branch names use lowercase kebab-case (e.g., `feature/book-search`).
3. One work item per branch (maps to one PR per the process rules).
4. Merge to `main` when the work item is complete and tested.
5. Delete the branch after merging.
