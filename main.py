import argparse
import logging
import os
import sys
from pathlib import Path

import fcntl

from src.service.service import AppService


def _setup_logging(level: str) -> None:
    """Configure root logging with a consistent format."""
    logging.basicConfig(
        level=getattr(logging, (level or "INFO").upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


def _acquire_lock(lock_path: str):
    """Acquire an exclusive, non-blocking file lock to prevent overlapping runs."""
    lock_file = open(lock_path, "w", encoding="utf-8")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise RuntimeError("Another instance is already running")
    return lock_file


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint. Returns a process exit code."""
    parser = argparse.ArgumentParser(description="AI Job Scraper")
    parser.add_argument(
        "--mode",
        choices=["scrape", "llm", "all"],
        default="all",
        help="Which flow to run: scrape (fetch+save), llm (score offers), all (both)",
    )
    parser.add_argument(
        "--candidate-path",
        default="data/candidate_data.txt",
        help="Path to candidate profile text file",
    )
    parser.add_argument(
        "--lock-file",
        default="/tmp/job_scraper.lock",
        help="Lockfile to prevent overlapping cron runs",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parent
    os.chdir(project_root)

    _setup_logging(args.log_level)
    logger = logging.getLogger("main")

    try:
        lock_handle = _acquire_lock(args.lock_file)
    except Exception as e:
        logger.error(f"Failed to acquire lock: {e}")
        return 2

    try:
        logger.info(f"Start AI Job Scraper (mode={args.mode})")
        app = AppService(path=args.candidate_path)
        app.run(mode=args.mode)
        logger.info("Done")
        return 0
    except Exception:
        logger.exception("Unhandled error during execution")
        return 1
    finally:
        try:
            lock_handle.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())