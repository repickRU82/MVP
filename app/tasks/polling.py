"""Background polling entrypoint (APScheduler/Celery to be wired in deployment)."""


def run_poll_cycle() -> None:
    # TODO: collect from IMAP, register in DB, upload to Nextcloud.
    return None
