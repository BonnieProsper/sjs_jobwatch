import pytest

@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

@pytest.fixture
def snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d
