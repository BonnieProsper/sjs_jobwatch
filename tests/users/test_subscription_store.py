from sjs_sitewatch.users.store import SubscriptionStore
from sjs_sitewatch.users.models import AlertSubscription


def test_store_roundtrip(temp_dir):
    path = temp_dir / "subs.json"
    store = SubscriptionStore(path)

    sub = AlertSubscription(
        email="a@test.com",
        frequency="daily",
        hour=9,
        ict_only=True,
        region=None,
    )

    store.save_all([sub])
    loaded = store.load_all()

    assert len(loaded) == 1
    assert loaded[0].email == sub.email
