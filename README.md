# AI Job Scraper

A script designed to:

- Scrape job offers (from JustJoinIt + NoFluffJobs).
- Save them to a persistent SQLite database.
- Evaluate candidate fit using an LLM (Groq) and append `ai_score` / `ai_summary`.

## Local Setup (Without Docker)

1. Create and activate a virtual environment (venv).

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file (minimal setup):

- `GROQ_API_KEY`
- `TELEGRAM_BOT_API_KEY` (optional)
- `TELEGRAM_CHAT_ID` (optional)

You can copy `.env.example` as a starting point.

4. Fill in your candidate profile details in `data/candidate_data.txt`.

## Running Locally

The `main.py` script supports different execution modes:

Scrape only + save to DB:

```bash
python main.py --mode scrape
```

LLM scoring only (for offers without `ai_summary`):

```bash
python main.py --mode llm
```

Full pipeline (Scrape + LLM):

```bash
python main.py --mode all
```

Available Options:

- `--candidate-path data/candidate_data.txt`
- `--lock-file /tmp/job_scraper.lock`
- `--log-level INFO`

## Automation Setup: Docker + CRON (VPS)

The easiest and safest deployment method on a VPS. Cron triggers a "one-shot" container based on a specific schedule.

### 1. Build the Image

Make sure you have a `.dockerignore` file in place, then build the image:

```bash
docker build -t job-scraper:latest .
```

### 2. Prepare Persistent Data Directories

Prepare a directory on your host machine for the SQLite database, candidate data, and the lock file.

- Host data path: `/opt/job-scraper/data/` (Place your `candidate_data.txt` here).
- Secrets: Create `/opt/job-scraper/.env` (Do not commit this to the repository!).

CRITICAL: Set the correct ownership so the non-root Docker user (`appuser` with ID `10001`) can write to the database:

```bash
mkdir -p /opt/job-scraper/data
sudo chown -R 10001:10001 /opt/job-scraper/data
```

### 3. Manual Test Run

Run this command to ensure the container works properly and can write to the database:

```bash
/usr/bin/docker run --rm \
    --env-file /opt/job-scraper/.env \
    -e DB_URL=sqlite:////app/data/jobs.db \
    -v /opt/job-scraper/data:/app/data \
    job-scraper:latest \
    --mode all \
    --candidate-path /app/data/candidate_data.txt \
    --lock-file /app/data/job_scraper.lock
```

Note: The `--lock-file` must point to the mounted volume (e.g. `/app/data/...`) because the `/tmp` directory inside the container is ephemeral and not shared between separate `docker run` executions.

### 4. Setup CRON Schedule

To automate the scraper to run Monday through Friday at 8:00, 12:00, 16:00, 20:00, and 00:00, add the following line to your system's crontab (`crontab -e`):

```cron
0 0,8,12,16,20 * * 1-5 /usr/bin/docker run --rm --env-file /opt/job-scraper/.env -e DB_URL=sqlite:////app/data/jobs.db -v /opt/job-scraper/data:/app/data job-scraper:latest --mode all --candidate-path /app/data/candidate_data.txt --lock-file /app/data/job_scraper.lock >> /opt/job-scraper/cron.log 2>&1
```
