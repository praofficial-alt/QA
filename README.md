# QA — POC

End-to-end QA automation with CI (GitHub Actions).

## Tech Stack

| Area | Choice |
|------|--------|
| **Language** | Python |
| **Framework** | Playwright / Appium |
| **API testing** | Postman (collections run via Newman in CI) |

## One machine: Dev + QA + GitHub sync

Use **this PC** for day‑to‑day development *and* for running the same checks you trust in CI (“QA on the desk”). **GitHub** runs **QA Pipeline** when you **push** (or open a PR) to `main` / `master`.

### One-time GitHub (repository)

1. **Remote** (already typical for this repo): `https://github.com/praofficial-alt/QA.git`  
2. **Actions enabled:** repo **Settings → Actions → General** → allow workflows.  
3. **Variable (optional):** **Settings → Secrets and variables → Actions → Variables** → `QA_BASE_URL` = URL Newman/pytest should hit (CI uses this; locally you can also set `BASE_URL` in the shell).  
4. **Secret (optional):** **Secrets** → `SLACK_WEBHOOK_URL` for Slack after the main job.  
5. **Branch:** push to **`main`** (and/or **`master`**) to match `.github/workflows/qa-pipeline.yml`.

### Recommended local setup (Windows)

```powershell
cd "d:\AI -Project\AI_POC\QA-main"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install --with-deps chromium
npm install -g newman
```

Point runs at your app (local or deployed):

```powershell
$env:BASE_URL = "https://your-app-or-localhost"
```

### Daily: develop → sync → pipeline runs on GitHub

```powershell
cd "d:\AI -Project\AI_POC\QA-main"
git pull origin main
# … edit tests / config …
git add -A
git status   # confirm only intended files (no secrets, no large .apk)
git commit -m "Describe your change"
git push origin main
```

Then open **GitHub → Actions → QA Pipeline** for the new run. **Artifacts** → **QA-Reports** (and the Appium job artifact if applicable).

### Authenticating `git push`

- **HTTPS:** GitHub may prompt for a [Personal Access Token](https://github.com/settings/tokens) as the password (not your GitHub account password).  
- **SSH:** add an SSH key to GitHub and use remote `git@github.com:praofficial-alt/QA.git`.

## Environment setup (local)

Equivalent to your toolchain; the repo pins versions in `requirements.txt` where possible.

```bash
# Python (pytest, pandas, openpyxl, Allure)
pip install -r requirements.txt

# Playwright browsers (after pip install playwright)
python -m playwright install --with-deps chromium

# Appium (Node) — for local server; CI installs inside the Android job
npm install -g appium@2
appium driver install uiautomator2

# Postman CLI
npm install -g newman
```

**Allure:** pytest writes raw results under `reports/allure` when you pass `--alluredir` (see below). Install the [Allure commandline](https://github.com/allure-framework/allure2), then open the HTML report locally:

```bash
python -m pytest tests/ -m "not appium" -v --alluredir=reports/allure
allure serve reports/allure
```

GitHub Actions uses the same `--alluredir=reports/allure` for both the **qa** and **appium-android** jobs (each job has its own workspace; download the matching artifact to run `allure serve` on that folder).

## CI flow (high level)

| Your step | Implemented as |
|-----------|----------------|
| Push code | `push` / `pull_request` / `workflow_dispatch` → **QA Pipeline** |
| API tests (Postman) | **`qa`** job: **Newman** first (`tests/api/postman/`) |
| UI tests | **Playwright** in **`qa`** (pytest, `-m "not appium"`). **Appium** in separate job **`appium-android`** (runs **in parallel** with `qa`, not strictly after Playwright). |
| Allure + Excel | **Allure** raw data from pytest (`--alluredir=reports/allure`). **Excel** via `python -m utils.excel_report` after API + UI. **Upload** artifact **QA-Reports**. |
| Notification | **Slack** at end of **`qa`** job (`SLACK_WEBHOOK_URL` optional). |

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

1. **Actions**: after push, open **Actions** → **QA Pipeline** and confirm the workflow runs (two jobs: **API + Playwright web**, and **Appium Android** — the mobile job uses an emulator and can take longer).
2. **Variable** `QA_BASE_URL`: **Settings → Secrets and variables → Actions → Variables** — set to your QA app URL (used by pytest and Newman). If unset, `https://example.com` is used.
3. **Manual run**: **Actions → QA Pipeline → Run workflow** — optional **base_url** overrides the variable for that run.
4. **Slack (optional):** add repository secret **`SLACK_WEBHOOK_URL`** (Incoming Webhook URL). After the **API (Newman) + UI (Playwright)** job finishes, the workflow posts a short message with **✅ / ❌**, **job conclusion**, and a **link to the run**. If the secret is missing, the step is skipped.

### Local runs

- **Install (web + API tooling + Excel):**  
  `pip install -r requirements.txt`
- **Web (Playwright) only** (no Appium):  
  `python -m pytest tests/ -m "not appium" -v --alluredir=reports/allure` then `allure serve reports/allure`
- **Optional login E2E** (`tests/ui/playwright/test_login.py`): off by default so CI stays green. To run it locally:  
  `E2E_LOGIN_ENABLED=1` plus `E2E_USERNAME`, `E2E_PASSWORD`. Optional: `E2E_LOGIN_PATH` (default `/login`), `E2E_USER_SELECTOR`, `E2E_PASS_SELECTOR`, `E2E_SUBMIT_SELECTOR`, `E2E_EXPECT_TITLE_CONTAINS` (default `Dashboard`).  
  Use **pytest-playwright** `page` / `base_url` (not raw `sync_playwright()` in tests) so behavior matches CI. Add `--alluredir=reports/allure` if you want Allure for that run.
- **Appium** (Android emulator + Appium server on `http://127.0.0.1:4723`):  
  `pip install -r requirements-appium.txt` then  
  `python -m pytest tests/ui/appium/ -m appium -v --alluredir=reports/allure` then `allure serve reports/allure`  
  If `Appium-Python-Client` fails to install on **Python 3.13** (common on Windows), use **Python 3.12** for that venv or rely on CI.  
  To skip Appium when running everything: set `SKIP_APPIUM_TESTS=1`.
- **Appium + local APK** (`tests/ui/appium/test_app_launch.py`): set **`APPIUM_APP`** to a path of your `.apk` (e.g. `android_superup_uat_0704.apk`). Optional **`APPIUM_DEVICE_NAME`** (default `Android`; use `emulator-5554` if needed). Uses **Appium 2** — use `http://127.0.0.1:4723`, **not** `.../wd/hub`. Without `APPIUM_APP`, the test is **skipped** (including default CI).

### Layout

| Path | Purpose |
|------|---------|
| `.github/workflows/qa-pipeline.yml` | CI (jobs: `qa`, `appium-android`) |
| `pytest.ini` | Pytest `testpaths`, `pythonpath`, markers (`appium`) |
| `playwright.config.py` | Playwright defaults (browser, timeout env) |
| `appium_config.py` | Appium capabilities (Android) |
| `utils/config.py` | Paths, `BASE_URL`, Appium server URL |
| `utils/excel_report.py` | `generate_report(rows)`; **`python -m utils.excel_report`** builds Excel from `reports/junit-*.xml` (CI step **Generate Excel report**) |
| `tests/ui/playwright/` | Web UI tests (Playwright) |
| `tests/ui/appium/` | Mobile UI tests (Appium) |
| `tests/api/postman/` | Postman `collection.json` + `qa.postman_environment.json` (not `postman_collection.json` at repo root) |
| `reports/api.json` | Newman JSON report (`-r cli,junit,json` in CI; gitignored) |
| `reports/allure/` | Allure raw results from pytest (`--alluredir=reports/allure`; use `allure serve reports/allure`) |
| `reports/excel/` | Excel reports |
| `reports/*.xml` | JUnit from CI (artifacts; gitignored) |
| `requirements.txt` | Playwright, pytest, pandas, openpyxl, allure-pytest (no Appium on 3.13) |
| `requirements-appium.txt` | Appium + pytest for mobile job / local Appium |
