from pathlib import Path
import tempfile
from typing import Iterator

import pytest


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)
