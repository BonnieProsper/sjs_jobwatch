import smtpd
import asyncore
import threading
import time
import pytest


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
