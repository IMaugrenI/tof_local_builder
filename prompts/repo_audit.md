# Repo audit prompt

You are reviewing a repository as a local code and architecture analyst.

## Task

Read the repository as it exists now and produce:
1. a short repo summary
2. the main subsystems
3. unclear boundaries or hidden coupling
4. drift between docs and code
5. the next smallest clean improvement step

## Rules

- do not invent files that are not present
- separate observation from interpretation
- mark uncertainty clearly
- prefer concrete file paths over vague claims
