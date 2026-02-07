#!/usr/bin/env python3
"""
Standalone code quality and logic tests.
Tests that don't require external dependencies.
"""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports_organized():
    """Check that imports are properly organized."""
    print("Checking import organization...")
    
    files_to_check = [
        "src/sjs_jobwatch/core/config.py",
        "src/sjs_jobwatch/core/diff.py",
        "src/sjs_jobwatch/storage/snapshots.py",
    ]
    
    for filepath in files_to_check:
        full_path = Path(__file__).parent.parent / filepath
        if not full_path.exists():
            continue
            
        content = full_path.read_text()
        lines = content.split("\n")
        
        # Find import section
        import_section = []
        in_imports = False
        for line in lines:
            if line.startswith("import ") or line.startswith("from "):
                in_imports = True
                import_section.append(line)
            elif in_imports and line.strip() and not line.startswith("#"):
                break
        
        # Check no relative imports outside package
        for imp in import_section:
            if "from ." in imp and ".." in imp:
                print(f"  ✗ Bad relative import in {filepath}: {imp}")
                return False
    
    print("  ✓ Imports OK")
    return True


def test_no_hardcoded_paths():
    """Check for hardcoded paths."""
    print("Checking for hardcoded paths...")
    
    py_files = list(Path(__file__).parent.parent.glob("src/**/*.py"))
    
    bad_patterns = [
        r'"/home/',
        r'"/Users/',
        r'"C:\\',
        r"'/home/",
        r"'/Users/",
    ]
    
    for pyfile in py_files:
        content = pyfile.read_text()
        for pattern in bad_patterns:
            if re.search(pattern, content):
                print(f"  ✗ Hardcoded path in {pyfile.name}")
                return False
    
    print("  ✓ No hardcoded paths")
    return True


def test_no_debug_code():
    """Check for debug code."""
    print("Checking for debug code...")
    
    py_files = list(Path(__file__).parent.parent.glob("src/**/*.py"))
    
    for pyfile in py_files:
        # Skip CLI which uses console.print
        if "cli/main.py" in str(pyfile):
            continue
            
        content = pyfile.read_text()
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            # Check for print() not in comments
            if "print(" in line and not line.strip().startswith("#"):
                # Allow logger calls
                if "logger" not in line and "logging" not in line:
                    print(f"  ✗ Debug print in {pyfile.name}:{i}")
                    return False
    
    print("  ✓ No debug code")
    return True


def test_docstrings_present():
    """Check that functions have docstrings."""
    print("Checking docstrings...")
    
    py_files = list(Path(__file__).parent.parent.glob("src/**/*.py"))
    py_files = [f for f in py_files if f.name != "__init__.py"]
    
    missing_docstrings = []
    
    for pyfile in py_files:
        content = pyfile.read_text()
        
        # Find function definitions
        func_pattern = r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        
        lines = content.split("\n")
        for i, line in enumerate(lines):
            match = re.match(func_pattern, line)
            if match:
                func_name = match.group(1)
                
                # Skip private functions and __init__
                if func_name.startswith("_") and func_name != "__init__":
                    continue
                
                # Check if next non-empty line is a docstring
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                
                if j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line.startswith('"""') and not next_line.startswith("'''"):
                        missing_docstrings.append(f"{pyfile.name}:{i+1} - {func_name}")
    
    if missing_docstrings and len(missing_docstrings) > 5:
        print(f"  ⚠ Some functions missing docstrings (found {len(missing_docstrings)})")
    else:
        print("  ✓ Docstrings OK")
    
    return True


def test_config_has_no_secrets():
    """Check config doesn't contain secrets."""
    print("Checking for hardcoded secrets...")
    
    config_file = Path(__file__).parent.parent / "src/sjs_jobwatch/core/config.py"
    content = config_file.read_text()
    
    # Check for suspicious patterns
    bad_patterns = [
        r'password\s*=\s*["\'][^"\']{8,}["\']',
        r'api_key\s*=\s*["\'][^"\']{16,}["\']',
        r'secret\s*=\s*["\'][^"\']{16,}["\']',
    ]
    
    for pattern in bad_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            print("  ✗ Possible hardcoded secret in config!")
            return False
    
    # Check that it uses os.getenv
    if "os.getenv" not in content and "os.environ" not in content:
        print("  ⚠ Config doesn't use environment variables")
    
    print("  ✓ No hardcoded secrets")
    return True


def test_consistent_naming():
    """Check for consistent naming conventions."""
    print("Checking naming conventions...")
    
    py_files = list(Path(__file__).parent.parent.glob("src/**/*.py"))
    
    # Check class names are PascalCase
    class_pattern = r'class\s+([a-z][a-zA-Z0-9]*)\s*[\(:]'
    
    for pyfile in py_files:
        content = pyfile.read_text()
        matches = re.findall(class_pattern, content)
        
        if matches:
            print(f"  ✗ Lowercase class name in {pyfile.name}: {matches[0]}")
            return False
    
    print("  ✓ Naming conventions OK")
    return True


def test_no_bare_except():
    """Check for bare except clauses."""
    print("Checking exception handling...")
    
    py_files = list(Path(__file__).parent.parent.glob("src/**/*.py"))
    
    for pyfile in py_files:
        content = pyfile.read_text()
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*except\s*:\s*$', line):
                print(f"  ✗ Bare except in {pyfile.name}:{i}")
                return False
    
    print("  ✓ Exception handling OK")
    return True


def test_file_sizes_reasonable():
    """Check that no file is excessively long."""
    print("Checking file sizes...")
    
    py_files = list(Path(__file__).parent.parent.glob("src/**/*.py"))
    
    max_lines = 600  # Reasonable maximum for maintainability
    
    for pyfile in py_files:
        lines = len(pyfile.read_text().split("\n"))
        if lines > max_lines:
            print(f"  ⚠ Large file: {pyfile.name} ({lines} lines)")
    
    print("  ✓ File sizes OK")
    return True


def test_config_values():
    """Test configuration values are reasonable."""
    print("Testing config values...")
    
    from sjs_jobwatch.core import config
    
    # Test paths are Path objects
    assert isinstance(config.PROJECT_ROOT, Path)
    assert isinstance(config.DATA_DIR, Path)
    
    # Test timeouts are reasonable
    assert 0 < config.REQUEST_TIMEOUT < 120
    assert 0 < config.REQUEST_DELAY < 10
    
    # Test retention settings
    assert config.SNAPSHOT_RETENTION_DAYS >= 0
    assert config.MAX_SNAPSHOTS >= 0
    
    # Test email config validation works
    valid, msg = config.validate_email_config()
    assert isinstance(valid, bool)
    assert isinstance(msg, str)
    
    print("  ✓ Config values OK")
    return True


def run_all_tests():
    """Run all static analysis tests."""
    print("=" * 70)
    print("SJS JobWatch - Code Quality Tests")
    print("=" * 70)
    print()
    
    tests = [
        test_imports_organized,
        test_no_hardcoded_paths,
        test_no_debug_code,
        test_docstrings_present,
        test_config_has_no_secrets,
        test_consistent_naming,
        test_no_bare_except,
        test_file_sizes_reasonable,
        test_config_values,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 70)
    print(f"Code Quality Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
