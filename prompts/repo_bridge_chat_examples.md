# Repo bridge chat examples

Use these after the Open WebUI repo_bridge tool has been added and enabled.

## Read the repo root

- `Use repo_tree on the root path and summarize the main areas.`

## Read one file

- `Use repo_read on MANIFEST.md and summarize the structure.`
- `Use repo_read on CODEX.md and extract the ethical core in short form.`

## Read then write

- `Use repo_read on MANIFEST.md, then write a short markdown summary to output/reviews/manifest_summary.md.`
- `Use repo_tree on docs/, identify likely important files, and write a small review plan to workspace/plans/docs_review.md.`

## Important boundary reminder

The tool should never write into the source repo.
It should only write into sandbox `workspace` or `output`.
