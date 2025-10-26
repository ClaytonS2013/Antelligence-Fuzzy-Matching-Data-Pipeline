# Antelligence Fuzzy Matching Data Pipeline

This project contains a data pipeline that leverages **GitHub Actions** to run a Python script on a schedule.  It packages your Python code, SQL queries and helper modules in a consistent layout and keeps secrets safe using GitHub’s built‑in vault.

## 📆 Repository structure

```
data-pipeline/
├─ dedupe_pipeline.py      # Main pipeline script
├─ utils/                  # Helper functions
│  └─ __init__.py
├─ sql/                    # SQL queries used by the pipeline
│  └─ sample.sql
├─ requirements.txt        # Python dependencies (or use pyproject.toml)
└─ .github/
    └─ workflows/
        └─ run.yml        # GitHub Actions workflow
```

## 🚀 Getting started

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/data-pipeline.git
   cd data-pipeline
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   # Or, if you have a pyproject.toml, run:
   # pip install .
   ```
3. **Configure your secrets**

   In your repository on GitHub, go to **Settings → Secrets and variables → Actions** and add the following secrets:

   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SMTP_USER`
   - `SMTP_PASS`
   - `SLACK_WEBHOOK`

   If you use other services, such as Google Cloud, add the appropriate secrets as well (e.g., `GOOGLE_SERVICE_ACCOUNT_JSON`).

## 🛠 How it works

The pipeline is orchestrated by GitHub Actions.  The workflow file `.github/workflows/run.yml` schedules the pipeline to run every day at **2:15 AM UTC** and allows manual runs from the **Actions** tab.

### ✍️ Workflow example (`run.yml`)

```yaml
name: Run pipeline

on:
  schedule:
    - cron: "15 2 * * *"  # every day at 2:15 AM UTC
  workflow_dispatch:       # manual trigger in the GitHub UI

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f pyproject.toml ]; then pip install .; fi

      - name: Run pipeline
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          SMTP_USER:     ${{ secrets.SMTP_USER }}
          SMTP_PASS:     ${{ secrets.SMTP_PASS }}
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
        run: |
          python dedupe_pipeline.py
```

## 📑 Main script (`dedupe_pipeline.py`)

Below is a minimal example of the main pipeline script.  It loads credentials from environment variables and can be extended to execute SQL queries, call APIs, deduplicate data and send notifications.

```python
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def main():
    print("Pipeline starting…")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY")
    # TODO: implement your pipeline logic here
    print("Connected to Supabase at:", SUPABASE_URL)
    print("All done!")

if __name__ == "__main__":
    main()
```

## 💃 SQL files

Store any SQL queries your pipeline uses in the `sql/` directory.  For example, `sample.sql` might contain:

```sql
-- put queries your script will load/execute
SELECT 1;
```

## ✅ Committing and pushing changes

After you add or modify files, commit and push them to your repository:

```bash
   git add .
   git commit -m "Initial pipeline structure and workflow"
   git push -u origin main
```

That’s it! Your pipeline will now run automatically on the schedule defined in `run.yml`, and you can manually trigger runs from the GitHub Actions tab.
