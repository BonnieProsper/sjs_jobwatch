from pathlib import Path
import logging

from sjs_sitewatch.scheduling.scheduler import start_scheduler


def test_scheduler_logs_startup(tmp_path, caplog):
    subscriptions = tmp_path / "subs.json"
    subscriptions.write_text(
        """
        [
          {
            "email": "test@example.com",
            "frequency": "daily",
            "hour": 9
          }
        ]
        """
    )

    caplog.set_level(logging.INFO)

    start_scheduler(
        data_dir=tmp_path,
        subscriptions_path=subscriptions,
        run_once=True,
    )

    messages = [r.message for r in caplog.records]

    assert any(
        "Scheduler started" in msg or "Starting" in msg
        for msg in messages
    )
