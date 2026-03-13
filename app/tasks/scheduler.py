from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.tasks.polling import run_poll_cycle

scheduler = BackgroundScheduler(timezone="UTC")


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(run_poll_cycle, "interval", minutes=settings.poll_interval_minutes, id="poll-mailboxes", replace_existing=True)
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
