from pathlib import Path

from sjs_sitewatch.scheduling.scheduler import start_scheduler
from sjs_sitewatch.users.models import AlertSubscription


def test_scheduler_run_once(monkeypatch, tmp_path):
    called = []

    def fake_job(**kwargs):
        called.append(kwargs["subscription"].email)

    monkeypatch.setattr(
        "sjs_sitewatch.scheduling.scheduler.run_alert_job",
        fake_job,
    )

    subs_path = tmp_path / "subs.json"
    subs_path.write_text(
        """
        [
          {
            "email": "test@example.com",
            "frequency": "daily",
            "hour": 12,
            "ict_only": true,
            "region": null,
            "min_severity": "medium"
          }
        ]
        """
    )

    start_scheduler(
        data_dir=Path("data"),
        subscriptions_path=subs_path,
        run_once=True,
    )

    assert called == ["test@example.com"]
