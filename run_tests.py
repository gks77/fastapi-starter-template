#!/usr/bin/env python3
"""
Test runner script for the FastAPI Users application.
This script provides an easy way to run tests with various options.
"""

import sys
import subprocess
import argparse
from typing import Optional


def run_tests(
    test_path: str = "tests/",
    coverage: bool = True,
    verbose: bool = True,
    markers: Optional[str] = None,
    parallel: bool = False,
    html_report: bool = False
):
    """Run tests with pytest."""
    cmd = ["python", "-m", "pytest"]
    
    # Add test path
    cmd.append(test_path)
    
    # Add coverage options
    if coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=xml"
        ])
        
        if html_report:
            cmd.append("--cov-report=html")
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add markers filter
    if markers:
        cmd.extend(["-m", markers])
    
    # Add parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--color=yes"
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd)


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for FastAPI Users application")
    
    parser.add_argument(
        "test_path",
        nargs="?",
        default="tests/",
        help="Path to test files or directory (default: tests/)"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Run tests without coverage reporting"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run tests in quiet mode (less verbose)"
    )
    
    parser.add_argument(
        "-m", "--markers",
        help="Run only tests matching given mark expression"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML coverage report"
    )
    
    args = parser.parse_args()
    
    # Run tests
    result = run_tests(
        test_path=args.test_path,
        coverage=not args.no_coverage,
        verbose=not args.quiet,
        markers=args.markers,
        parallel=args.parallel,
        html_report=args.html_report
    )
    
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
