import os

from sjs_sitewatch.alerts.sinks.email import EmailSink
from sjs_sitewatch.alerts.models import ScoredChange, Severity
from sjs_sitewatch.domain.diff import JobChange


def test_email_sink_sends_via_fake_smtp(fake_smtp_server, monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "127.0.0.1")
    monkeypatch.setenv("SMTP_PORT", "1025")
    monkeypatch.setenv("GMAIL_ADDRESS", "sender@test.com")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "password")

    change = ScoredChange(
        change=JobChange(
            job_id="job-1",
            before=None,
            after=None,
            changes=[],
        ),
        severity=Severity.HIGH,
        reason="Test alert",
    )

    sink = EmailSink(to_email="test@example.com")
    sink.send([change])

    assert len(fake_smtp_server.messages) == 1
