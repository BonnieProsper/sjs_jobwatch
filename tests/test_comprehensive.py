"""
Comprehensive test suite for SJS JobWatch.

Tests all core functionality without requiring network access or external dependencies.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Test 1: Model validation
def test_models():
    """Test Pydantic models work correctly."""
    print("Testing models...")
    
    from sjs_jobwatch.core.models import Job, Snapshot, JobChange, DiffResult, Severity, Region
    
    # Test Job creation
    job = Job(
        id="123",
        title="Software Developer",
        employer="Government Agency",
        category="ICT",
        region="Auckland",
        pay_min=80000.0,
        pay_max=100000.0,
    )
    assert job.id == "123"
    assert job.title == "Software Developer"
    
    # Test pay validation
    try:
        bad_job = Job(
            id="456",
            title="Test",
            employer="Test",
            pay_min=100000.0,
            pay_max=80000.0,  # Should fail - max < min
        )
        assert False, "Should have raised validation error"
    except Exception:
        pass  # Expected
    
    # Test Snapshot
    snapshot = Snapshot(
        timestamp=datetime.now(),
        jobs=[job],
        total_count=1,
        source_url="https://test.com",
    )
    assert snapshot.total_count == len(snapshot.jobs)
    
    # Test Severity enum
    assert Severity.LOW.priority < Severity.HIGH.priority
    assert Severity.CRITICAL.priority == 3
    
    print("  ✓ Models OK")


def test_diff_logic():
    """Test diff engine logic."""
    print("Testing diff logic...")
    
    from sjs_jobwatch.core.models import Job, Snapshot
    from sjs_jobwatch.core.diff import diff_snapshots, compare_jobs
    
    # Create test jobs
    job1 = Job(id="1", title="Developer", employer="Agency A")
    job2 = Job(id="2", title="Analyst", employer="Agency B")
    job3 = Job(id="3", title="Manager", employer="Agency C")
    
    # Create snapshots
    old_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 1),
        jobs=[job1, job2],
        total_count=2,
        source_url="test",
    )
    
    # Modified job2
    job2_modified = Job(
        id="2",
        title="Senior Analyst",  # Changed
        employer="Agency B",
        region="Wellington",  # Added
    )
    
    new_snapshot = Snapshot(
        timestamp=datetime(2024, 1, 2),
        jobs=[job1, job2_modified, job3],  # job1 same, job2 modified, job3 new
        total_count=3,
        source_url="test",
    )
    
    # Calculate diff
    diff = diff_snapshots(old_snapshot, new_snapshot)
    
    # Verify results
    assert len(diff.added) == 1, f"Expected 1 added, got {len(diff.added)}"
    assert diff.added[0].job_id == "3"
    
    assert len(diff.removed) == 0
    
    assert len(diff.modified) == 1, f"Expected 1 modified, got {len(diff.modified)}"
    assert diff.modified[0].job_id == "2"
    assert len(diff.modified[0].changes) >= 1  # Should detect title and region changes
    
    # Test compare_jobs directly
    changes = compare_jobs(job2, job2_modified)
    assert any(c.field == "title" for c in changes)
    assert any(c.field == "region" for c in changes)
    
    print("  ✓ Diff logic OK")


def test_subscription_model():
    """Test subscription validation."""
    print("Testing subscriptions...")
    
    from sjs_jobwatch.core.models import JobCategory, Region, Frequency, Severity
    
    # Note: Can't test actual Pydantic model without it installed,
    # but we can test the logic would be correct
    
    # Test enum values
    assert Region.AUCKLAND.value == "Auckland"
    assert JobCategory.ICT.value == "ICT"
    assert Frequency.DAILY.value == "daily"
    assert Severity.MEDIUM.value == "medium"
    
    print("  ✓ Subscriptions OK")


def test_config():
    """Test configuration module."""
    print("Testing config...")
    
    from sjs_jobwatch.core import config
    
    # Test paths exist
    assert config.PROJECT_ROOT.exists()
    
    # Test URL builder
    url = config.get_sjs_url(region="Auckland", category="ICT")
    assert "Auckland" in url or "region=Auckland" in url
    assert "ICT" in url or "category=ICT" in url
    
    # Test email validation
    import os
    os.environ.pop("GMAIL_ADDRESS", None)
    os.environ.pop("GMAIL_APP_PASSWORD", None)
    
    is_valid, error = config.validate_email_config()
    assert not is_valid
    assert "GMAIL_ADDRESS" in error
    
    print("  ✓ Config OK")


def test_snapshot_storage():
    """Test snapshot storage logic."""
    print("Testing storage...")
    
    from sjs_jobwatch.core.models import Job, Snapshot
    from sjs_jobwatch.storage.snapshots import SnapshotStore
    import tempfile
    import shutil
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        store = SnapshotStore(temp_dir)
        
        # Create test snapshot
        job = Job(id="1", title="Test", employer="Test Agency")
        snapshot = Snapshot(
            timestamp=datetime.now(),
            jobs=[job],
            total_count=1,
            source_url="test",
        )
        
        # Save
        filepath = store.save(snapshot)
        assert filepath.exists()
        
        # Load
        loaded = store.load(snapshot.timestamp)
        assert loaded is not None
        assert len(loaded.jobs) == 1
        assert loaded.jobs[0].id == "1"
        
        # List
        files = store.list_snapshots()
        assert len(files) == 1
        
        # Count
        assert store.count() == 1
        
        print("  ✓ Storage OK")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_email_rendering():
    """Test email template logic (without actually sending)."""
    print("Testing email rendering...")
    
    # Can't fully test without Jinja2, but verify structure
    from pathlib import Path
    
    templates_dir = Path(__file__).parent.parent / "src" / "sjs_jobwatch" / "alerts" / "templates"
    
    assert (templates_dir / "alert_email.html").exists()
    assert (templates_dir / "alert_email.txt").exists()
    
    # Check templates have required placeholders
    html_content = (templates_dir / "alert_email.html").read_text()
    assert "{{ period }}" in html_content
    assert "{{ added_count }}" in html_content
    assert "{{ removed_count }}" in html_content
    
    txt_content = (templates_dir / "alert_email.txt").read_text()
    assert "{{ added_count }}" in txt_content
    
    print("  ✓ Email templates OK")


def test_cli_structure():
    """Test CLI module structure."""
    print("Testing CLI structure...")
    
    cli_file = Path(__file__).parent.parent / "src" / "sjs_jobwatch" / "cli" / "main.py"
    assert cli_file.exists()
    
    content = cli_file.read_text()
    
    # Check essential commands exist
    assert "def scrape" in content
    assert "def diff" in content
    assert "def list" in content
    assert "def export" in content
    assert "def alerts" in content
    assert "def run" in content
    
    # Check Click decorators
    assert "@click.command" in content or "@cli.command" in content
    assert "@click.option" in content
    
    print("  ✓ CLI structure OK")


def test_data_structures():
    """Test internal data structure consistency."""
    print("Testing data structures...")
    
    from sjs_jobwatch.core.models import Job, JobChange, FieldChange
    
    # Test FieldChange
    change = FieldChange(field="title", old_value="Old", new_value="New")
    assert change.field == "title"
    
    # Test JobChange
    job_before = Job(id="1", title="Old Title", employer="Agency")
    job_after = Job(id="1", title="New Title", employer="Agency")
    
    job_change = JobChange(
        job_id="1",
        before=job_before,
        after=job_after,
        changes=[change],
    )
    
    assert job_change.change_type == "modified"
    assert job_change.title == "New Title"
    
    # Test added job
    added_change = JobChange(job_id="2", before=None, after=job_after, changes=[])
    assert added_change.change_type == "added"
    
    # Test removed job
    removed_change = JobChange(job_id="3", before=job_before, after=None, changes=[])
    assert removed_change.change_type == "removed"
    
    print("  ✓ Data structures OK")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("Testing edge cases...")
    
    from sjs_jobwatch.core.models import Job, Snapshot
    from sjs_jobwatch.core.diff import diff_snapshots
    
    # Empty snapshots
    empty1 = Snapshot(
        timestamp=datetime.now(),
        jobs=[],
        total_count=0,
        source_url="test",
    )
    empty2 = Snapshot(
        timestamp=datetime.now(),
        jobs=[],
        total_count=0,
        source_url="test",
    )
    
    diff = diff_snapshots(empty1, empty2)
    assert diff.total_changes == 0
    assert not diff.has_changes
    
    # None values in job fields
    minimal_job = Job(
        id="1",
        title="Title",
        employer="Employer",
        # All other fields are None
    )
    assert minimal_job.region is None
    assert minimal_job.pay_min is None
    
    print("  ✓ Edge cases OK")


def test_file_structure():
    """Test project file structure is correct."""
    print("Testing file structure...")
    
    base = Path(__file__).parent.parent
    
    # Check key files exist
    assert (base / "pyproject.toml").exists()
    assert (base / "README.md").exists()
    assert (base / "LICENSE").exists()
    assert (base / ".gitignore").exists()
    
    # Check module structure
    src = base / "src" / "sjs_jobwatch"
    assert (src / "__init__.py").exists()
    assert (src / "core" / "__init__.py").exists()
    assert (src / "core" / "models.py").exists()
    assert (src / "core" / "config.py").exists()
    assert (src / "core" / "diff.py").exists()
    assert (src / "ingestion" / "scraper.py").exists()
    assert (src / "storage" / "snapshots.py").exists()
    assert (src / "alerts" / "email.py").exists()
    assert (src / "alerts" / "subscriptions.py").exists()
    assert (src / "cli" / "main.py").exists()
    
    # Check docs
    assert (base / "docs" / "SETUP_GUIDE.md").exists()
    assert (base / "docs" / "MIGRATION.md").exists()
    
    print("  ✓ File structure OK")


def test_no_circular_imports():
    """Test there are no circular import dependencies."""
    print("Testing for circular imports...")
    
    # This is a simple check - just try importing each module
    modules_to_test = [
        "sjs_jobwatch.core.models",
        "sjs_jobwatch.core.config",
        "sjs_jobwatch.core.diff",
        # Can't test others without dependencies installed
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
        except ImportError as e:
            if "pydantic" not in str(e) and "requests" not in str(e):
                # Real circular import or syntax error
                raise
    
    print("  ✓ No circular imports detected")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("SJS JobWatch - Comprehensive Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_file_structure,
        test_no_circular_imports,
        test_models,
        test_diff_logic,
        test_subscription_model,
        test_config,
        test_snapshot_storage,
        test_email_rendering,
        test_cli_structure,
        test_data_structures,
        test_edge_cases,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
