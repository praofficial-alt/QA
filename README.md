# QA — POC

Python **Playwright** (UI) + **Postman/Newman** (API) + GitHub Actions.

## Repo

Remote: [github.com/praofficial-alt/QA](https://github.com/praofficial-alt/QA)

### First-time push (local folder)

```bash
git init
git branch -M main
git remote add origin https://github.com/praofficial-alt/QA.git
git add .
git commit -m "Add QA pipeline, tests, Postman collection"
git push -u origin main
```

If the remote already has commits, use `git pull origin main --rebase` before pushing, or merge as needed.

### GitHub configuration

1. **Actions**: after push, open **Actions** → **QA Pipeline** and confirm the workflow runs.
2. **Variable** `QA_BASE_URL`: **Settings → Secrets and variables → Actions → Variables** — set to your QA app URL (used by pytest and Newman). If unset, `https://example.com` is used.
3. **Manual run**: **Actions → QA Pipeline → Run workflow** — optional **base_url** overrides the variable for that run.

### Layout

| Path | Purpose |
|------|---------|
| `.github/workflows/qa-pipeline.yml` | CI |
| `tests/` | pytest + Playwright |
| `postman/collection.json` | Newman (API); edit or replace with your export |
| `reports/` | JUnit XML from CI (artifact) |
