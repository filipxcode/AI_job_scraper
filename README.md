# AI Job Scraper

Skrypt do:
- scrapowania ofert (JustJoinIt + NoFluffJobs),
- zapisywania ich do SQLite,
- oceniania dopasowania kandydata przez LLM (Groq) i dopisywania `ai_score`/`ai_summary`.

## Setup

1) Utwórz i aktywuj venv

2) Zainstaluj zależności:

`pip install -r requirements.txt`

3) Ustaw `.env` (minimalnie):

- `GROQ_API_KEY`
- `TELEGRAM_BOT_API_KEY` (jeśli używasz)
- `TELEGRAM_CHAT_ID` (jeśli używasz)

4) Uzupełnij dane kandydata w `data/candidate_data.txt`.

## Uruchamianie

`main.py` ma tryby uruchomienia:

- Tylko scrape + zapis do DB:

`python main.py --mode scrape`

- Tylko LLM scoring ofert bez `ai_summary`:

`python main.py --mode llm`

- Pełny pipeline:

`python main.py --mode all`

Opcje:
- `--candidate-path data/candidate_data.txt`
- `--lock-file /tmp/job_scraper.lock`
- `--log-level INFO`

## CRON (VPS)

Przykład (co 30 minut):

`*/30 * * * * cd /home/master_g/projects/JobScraper && /home/master_g/projects/JobScraper/venv/bin/python main.py --mode all >> /var/log/job_scraper.log 2>&1`

Lockfile domyślnie blokuje nakładanie się uruchomień.
# AI_job_scraper
