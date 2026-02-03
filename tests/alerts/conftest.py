import smtpd
import asyncore
import threading
import time
import pytest

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

@pytest.fixture
def sample_snapshots(tmp_path):
    prev = tmp_path / "prev.json"
    curr = tmp_path / "curr.json"

    prev.write_text(PREV_SNAPSHOT_JSON)
    curr.write_text(CURR_SNAPSHOT_JSON)

    return prev, curr



class DummySMTPServer(smtpd.SMTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = []

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        self.messages.append(data)


@pytest.fixture
def fake_smtp_server():
    server = DummySMTPServer(("127.0.0.1", 1025), None)

    thread = threading.Thread(target=asyncore.loop, daemon=True)
    thread.start()
    time.sleep(0.1)

    yield server

    server.close()
