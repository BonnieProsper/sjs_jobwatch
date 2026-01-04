from sjs_sitewatch.alerts import select_alerts
from sjs_sitewatch.domain.diff import JobDiff
from sjs_sitewatch.emailer import send_email


def send_daily_ict_summary(diff: JobDiff) -> None:
    payload = select_alerts(diff, ict_only=True)

    if not payload["added"] and not payload["updated"]:
        return  # Avoid spam

    lines: list[str] = []
    lines.append("📊 Daily ICT Job Summary\n")

    if payload["added"]:
        lines.append(f"🆕 New ICT jobs: {len(payload['added'])}")

    if payload["updated"]:
        lines.append(f"✏️ Updated ICT jobs: {len(payload['updated'])}")

    send_email(
        subject="Daily ICT Job Watch",
        body="\n".join(lines),
    )
