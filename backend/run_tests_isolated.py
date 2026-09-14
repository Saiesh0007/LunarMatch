#!/usr/bin/env python
"""Run full pytest suite with per-file process isolation for Windows stability.

Windows cannot fork() processes, so pytest-xdist's --forked doesn't work.
The heavy native libraries (cv2, numpy, rasterio) accumulate resources that
cause access violations when all 76 tests run in a single process.

This runner executes each test file in a separate process, so a crash in one
file doesn't affect the others. Results are aggregated at the end.

If a test file crashes in batch mode (native access violation), the runner
automatically retries each test in the file individually in its own process.

Usage:
    python run_tests_isolated.py
"""
import subprocess
import sys
import os
import gc
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
test_dir = backend_dir / "tests"

# Test files in a sensible order (lightweight first, heavy last)
test_files = sorted(
    f.name for f in test_dir.glob("test_*.py")
)

total_files_passed = 0
total_files_failed = 0
total_files_crashed = 0
failures = []
crashes = []
individual_crashes = []

env = os.environ.copy()
env["PYTHONFAULTHANDLER"] = "1"


def run_tests_individually(test_file_name):
    """Run each test in a file individually in its own subprocess.

    This is the fallback when a test file crashes in batch mode.
    Returns (passed_count, crashed_list).
    """
    # First, collect test node IDs
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         str(test_dir / test_file_name),
         "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=str(backend_dir),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    # Parse test node IDs from output (format: "tests/test_file.py::test_name")
    test_ids = []
    for line in result.stdout.strip().split("\n"):
        line = line.strip()
        if "::" in line and not line.startswith("test_session"):
            test_ids.append(line)

    passed = 0
    crashed = []
    for test_id in test_ids:
        try:
            r = subprocess.run(
                [sys.executable, "-X", "faulthandler", "-m", "pytest",
                 test_id, "-v", "--tb=short", "-p", "no:cacheprovider"],
                cwd=str(backend_dir),
                capture_output=True,
                text=True,
                env=env,
                timeout=300,
            )
            if r.returncode == 0:
                passed += 1
                print(f"    -> {test_id}: PASSED")
            else:
                crashed.append(f"{test_id} (exit code {r.returncode})")
                print(f"    -> {test_id}: CRASHED (exit code {r.returncode})")
        except subprocess.TimeoutExpired:
            crashed.append(f"{test_id} (timeout)")
            print(f"    -> {test_id}: TIMEOUT")
        except Exception as e:
            crashed.append(f"{test_id} (error: {e})")
            print(f"    -> {test_id}: ERROR ({e})")

    return passed, crashed


for test_file in test_files:
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print(f"{'='*60}", flush=True)

    try:
        result = subprocess.run(
            [sys.executable, "-X", "faulthandler", "-m", "pytest",
             str(test_dir / test_file),
             "-v", "--tb=short", "-p", "no:cacheprovider"],
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
            env=env,
            timeout=300,
        )
        # Print output (both stdout and stderr)
        if result.stdout:
            print(result.stdout, flush=True)
        if result.stderr:
            print(result.stderr, flush=True)

        if result.returncode == 0:
            print(f"  -> {test_file}: PASSED", flush=True)
            total_files_passed += 1
        elif result.returncode < 0 or result.returncode >= 0x80000000:
            # Process was killed by signal or crashed (native access violation)
            # On Windows, access violations produce exit codes like 3221225477 (0xC0000005)
            # Try running tests individually as a fallback
            print(f"  -> {test_file}: CRASHED in batch mode, trying individual tests...", flush=True)
            passed, crashed = run_tests_individually(test_file)
            if len(crashed) == 0:
                print(f"  -> {test_file}: PASSED (individual tests)", flush=True)
                total_files_passed += 1
            else:
                total_files_crashed += 1
                crashes.append(test_file)
                individual_crashes.extend(crashed)
                print(f"  -> {test_file}: CRASHED ({len(crashed)} individual failures)", flush=True)
        else:
            total_files_failed += 1
            failures.append(test_file)
            print(f"  -> {test_file}: FAILED (exit code {result.returncode})", flush=True)
    except subprocess.TimeoutExpired:
        total_files_crashed += 1
        crashes.append(test_file)
        print(f"  -> {test_file}: TIMEOUT", flush=True)
    except Exception as e:
        total_files_crashed += 1
        crashes.append(test_file)
        print(f"  -> {test_file}: ERROR ({e})", flush=True)

    # Clean up Python objects and wait briefly for OS to reclaim native memory
    # This helps prevent intermittent Windows access violations caused by
    # native libraries (cv2, numpy, rasterio) in a memory-pressured state
    gc.collect()
    time.sleep(0.5)

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"  Test files passed: {total_files_passed}/{len(test_files)}")
print(f"  Failed:     {total_files_failed}")
print(f"  Crashed:    {total_files_crashed}")

if failures:
    print(f"\nFailed files:")
    for f in failures:
        print(f"  - {f}")

if crashes:
    print(f"\nCrashed files:")
    for c in crashes:
        print(f"  - {c}")

if individual_crashes:
    print(f"\nIndividual crashes:")
    for c in individual_crashes:
        print(f"  - {c}")

exit_code = 0 if total_files_crashed == 0 and total_files_failed == 0 else 1
sys.exit(exit_code)
