import asyncio
import logging

from telegram import Bot

from ..config.settings import get_settings


logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.TELEGRAM_BOT_API_KEY or not settings.TELEGRAM_CHAT_ID:
            raise RuntimeError("Telegram is not configured (missing TELEGRAM_BOT_API_KEY/TELEGRAM_CHAT_ID)")

        token = settings.TELEGRAM_BOT_API_KEY
        self._bot = Bot(token=token)
        self._chat_id = settings.TELEGRAM_CHAT_ID

    async def send_message_async(self, text: str) -> None:
        await self._bot.send_message(chat_id=self._chat_id, text=text)

    def send_message(self, text: str) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self.send_message_async(text))
            return
        loop.create_task(self.send_message_async(text))

def format_offer_message(title: str, company: str, score: int | None, summary: str | None, url: str) -> str:
    header = f"{title} — {company}".strip(" —")
    score_line = f"Score: {score}/10" if score is not None else "Score: n/a"
    summary_line = summary or ""
    return "\n".join([line for line in [header, score_line, summary_line, url] if line])
