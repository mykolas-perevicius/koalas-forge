#!/usr/bin/env python3
"""
🐨 Koala's Forge - Comprehensive Testing Suite
Interactive walkthrough and automated testing of all features
"""

import asyncio
import subprocess
import time
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any
import json


class Colors:
    """Terminal colors for pretty output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestResult:
    """Test result tracking"""
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []
        self.start_time = None
        self.end_time = None

    def add_pass(self):
        self.passed += 1

    def add_fail(self, error: str):
        self.failed += 1
        self.errors.append(error)

    def add_skip(self):
        self.skipped += 1

    @property
    def total(self):
        return self.passed + self.failed + self.skipped

    @property
    def success_rate(self):
        if self.total == 0:
            return 0
        return (self.passed / self.total) * 100


class KoalaTestSuite:
    """Comprehensive test suite for Koala's Forge"""

    def __init__(self):
        self.results = []
        self.interactive = True
        self.verbose = True
        self.test_package = "tree"  # Simple package for testing
        self.koala_path = "./koala"

    def print_header(self, text: str):
        """Print a section header"""
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}🐨 {text}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

    def print_test(self, name: str, status: str = "RUNNING"):
        """Print test status"""
        if status == "PASS":
            symbol = "✅"
            color = Colors.GREEN
        elif status == "FAIL":
            symbol = "❌"
            color = Colors.FAIL
        elif status == "SKIP":
            symbol = "⏭️"
            color = Colors.WARNING
        else:
            symbol = "🔄"
            color = Colors.BLUE

        print(f"{color}{symbol} {name}{Colors.ENDC}")

    def run_command(self, cmd: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def wait_for_input(self, prompt: str = "Press Enter to continue..."):
        """Wait for user input in interactive mode"""
        if self.interactive:
            input(f"\n{Colors.CYAN}{prompt}{Colors.ENDC}")

    async def test_basic_commands(self) -> TestResult:
        """Test basic CLI commands"""
        result = TestResult("Basic Commands")
        result.start_time = time.time()

        self.print_header("Testing Basic Commands")

        tests = [
            (["./koala", "--help"], "Help command"),
            (["./koala", "version"], "Version command"),
            (["./koala", "status"], "Status command"),
            (["./koala", "categories"], "Categories listing"),
            (["./koala", "health"], "Health check"),
        ]

        for cmd, description in tests:
            print(f"\n📌 Testing: {description}")
            print(f"   Command: {' '.join(cmd)}")

            success, stdout, stderr = self.run_command(cmd)

            if success:
                self.print_test(description, "PASS")
                result.add_pass()
                if self.verbose and stdout:
                    print(f"{Colors.CYAN}Output preview:{Colors.ENDC}")
                    print(stdout[:200] + "..." if len(stdout) > 200 else stdout)
            else:
                self.print_test(description, "FAIL")
                result.add_fail(f"{description}: {stderr}")
                print(f"{Colors.FAIL}Error: {stderr}{Colors.ENDC}")

        result.end_time = time.time()
        return result

    async def test_package_management(self) -> TestResult:
        """Test package installation, update, and removal"""
        result = TestResult("Package Management")
        result.start_time = time.time()

        self.print_header("Testing Package Management")

        print("We'll test with a small, safe package: 'tree'")
        self.wait_for_input()

        # Search for package
        print(f"\n📌 Testing: Package search")
        cmd = ["./koala", "search", "tree"]
        success, stdout, stderr = self.run_command(cmd)
        if success:
            self.print_test("Search functionality", "PASS")
            result.add_pass()
        else:
            self.print_test("Search functionality", "FAIL")
            result.add_fail(f"Search failed: {stderr}")

        # Get package info
        print(f"\n📌 Testing: Package info")
        cmd = ["./koala", "info", self.test_package]
        success, stdout, stderr = self.run_command(cmd)
        if success:
            self.print_test("Package info", "PASS")
            result.add_pass()
        else:
            self.print_test("Package info", "FAIL")
            result.add_fail(f"Info failed: {stderr}")

        # Install package
        print(f"\n📌 Testing: Package installation")
        print(f"   Installing {self.test_package}...")
        cmd = ["./koala", "install", self.test_package, "-y"]
        success, stdout, stderr = self.run_command(cmd, timeout=60)
        if success:
            self.print_test("Package installation", "PASS")
            result.add_pass()
        else:
            self.print_test("Package installation", "FAIL")
            result.add_fail(f"Installation failed: {stderr}")

        # Verify installation
        print(f"\n📌 Testing: Package verification")
        cmd = ["./koala", "verify", self.test_package]
        success, stdout, stderr = self.run_command(cmd)
        if success:
            self.print_test("Package verification", "PASS")
            result.add_pass()
        else:
            self.print_test("Package verification", "FAIL")
            result.add_fail(f"Verification failed: {stderr}")

        # Uninstall package
        if self.interactive:
            confirm = input(f"\n{Colors.WARNING}Uninstall {self.test_package}? (y/n): {Colors.ENDC}")
            if confirm.lower() == 'y':
                print(f"\n📌 Testing: Package removal")
                cmd = ["./koala", "uninstall", self.test_package, "-y"]
                success, stdout, stderr = self.run_command(cmd)
                if success:
                    self.print_test("Package removal", "PASS")
                    result.add_pass()
                else:
                    self.print_test("Package removal", "FAIL")
                    result.add_fail(f"Removal failed: {stderr}")

        result.end_time = time.time()
        return result

    async def test_advanced_features(self) -> TestResult:
        """Test advanced features like dependencies, recovery, recommendations"""
        result = TestResult("Advanced Features")
        result.start_time = time.time()

        self.print_header("Testing Advanced Features")

        # Test dependency resolution
        print(f"\n📌 Testing: Dependency analysis")
        cmd = ["./koala", "deps", "docker", "nodejs"]
        success, stdout, stderr = self.run_command(cmd)
        if success:
            self.print_test("Dependency resolution", "PASS")
            result.add_pass()
            if self.verbose:
                print(f"{Colors.CYAN}Dependencies found:{Colors.ENDC}")
                print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
        else:
            self.print_test("Dependency resolution", "FAIL")
            result.add_fail(f"Dependency analysis failed: {stderr}")

        # Test recommendations
        print(f"\n📌 Testing: Smart recommendations")
        cmd = ["./koala", "recommend"]
        success, stdout, stderr = self.run_command(cmd)
        if success or "No packages installed" in stdout:
            self.print_test("Recommendations", "PASS")
            result.add_pass()
        else:
            self.print_test("Recommendations", "FAIL")
            result.add_fail(f"Recommendations failed: {stderr}")

        # Test recovery plan
        print(f"\n📌 Testing: Recovery planning")
        cmd = ["./koala", "recover", "docker"]
        success, stdout, stderr = self.run_command(cmd)
        if success:
            self.print_test("Recovery planning", "PASS")
            result.add_pass()
        else:
            self.print_test("Recovery planning", "FAIL")
            result.add_fail(f"Recovery failed: {stderr}")

        result.end_time = time.time()
        return result

    async def test_history_and_privacy(self) -> TestResult:
        """Test history tracking and privacy features"""
        result = TestResult("History & Privacy")
        result.start_time = time.time()

        self.print_header("Testing History & Privacy Features")

        # Test history
        print(f"\n📌 Testing: Installation history")
        cmd = ["./koala", "history", "--limit", "10"]
        success, stdout, stderr = self.run_command(cmd)
        if success:
            self.print_test("History tracking", "PASS")
            result.add_pass()
        else:
            self.print_test("History tracking", "FAIL")
            result.add_fail(f"History failed: {stderr}")

        # Test privacy status
        print(f"\n📌 Testing: Privacy settings")
        cmd = ["./koala", "privacy", "status"]
        success, stdout, stderr = self.run_command(cmd)
        if success:
            self.print_test("Privacy status", "PASS")
            result.add_pass()
        else:
            self.print_test("Privacy status", "FAIL")
            result.add_fail(f"Privacy status failed: {stderr}")

        # Test breakage detection
        print(f"\n📌 Testing: Breakage detection")
        cmd = ["./koala", "breakages", "--days", "7"]
        success, stdout, stderr = self.run_command(cmd)
        if success:
            self.print_test("Breakage detection", "PASS")
            result.add_pass()
        else:
            self.print_test("Breakage detection", "FAIL")
            result.add_fail(f"Breakage detection failed: {stderr}")

        result.end_time = time.time()
        return result

    async def test_self_test(self) -> TestResult:
        """Run the built-in self-test"""
        result = TestResult("Self-Test")
        result.start_time = time.time()

        self.print_header("Running Built-in Self-Test")

        print("This will run Koala's comprehensive self-test...")
        self.wait_for_input()

        cmd = ["./koala", "self-test"]
        success, stdout, stderr = self.run_command(cmd, timeout=60)

        if success:
            self.print_test("Self-test execution", "PASS")
            result.add_pass()

            # Parse self-test results
            if "Test Results:" in stdout:
                lines = stdout.split('\n')
                for line in lines:
                    if "Passed:" in line:
                        print(f"{Colors.GREEN}{line}{Colors.ENDC}")
                    elif "Failed:" in line:
                        print(f"{Colors.FAIL}{line}{Colors.ENDC}")
        else:
            self.print_test("Self-test execution", "FAIL")
            result.add_fail(f"Self-test failed: {stderr}")

        result.end_time = time.time()
        return result

    async def test_import_export(self) -> TestResult:
        """Test import/export functionality"""
        result = TestResult("Import/Export")
        result.start_time = time.time()

        self.print_header("Testing Import/Export Features")

        # Test export
        print(f"\n📌 Testing: Export to file")
        export_file = "test_export.txt"
        cmd = ["./koala", "export", export_file]
        success, stdout, stderr = self.run_command(cmd)

        if success and os.path.exists(export_file):
            self.print_test("Export functionality", "PASS")
            result.add_pass()

            # Show exported content
            with open(export_file, 'r') as f:
                content = f.read()
                print(f"{Colors.CYAN}Exported {len(content.split())} packages{Colors.ENDC}")

            # Cleanup
            os.remove(export_file)
        else:
            self.print_test("Export functionality", "FAIL")
            result.add_fail(f"Export failed: {stderr}")

        # Test list installed
        print(f"\n📌 Testing: List installed packages")
        cmd = ["./koala", "list", "--installed"]
        success, stdout, stderr = self.run_command(cmd, timeout=60)
        if success:
            self.print_test("List installed", "PASS")
            result.add_pass()
        else:
            self.print_test("List installed", "FAIL")
            result.add_fail(f"List installed failed: {stderr}")

        result.end_time = time.time()
        return result

    async def test_rollback_system(self) -> TestResult:
        """Test rollback/snapshot functionality"""
        result = TestResult("Rollback System")
        result.start_time = time.time()

        self.print_header("Testing Rollback System")

        # List snapshots
        print(f"\n📌 Testing: List snapshots")
        cmd = ["./koala", "rollback", "list"]
        success, stdout, stderr = self.run_command(cmd)
        if success:
            self.print_test("List snapshots", "PASS")
            result.add_pass()
        else:
            self.print_test("List snapshots", "FAIL")
            result.add_fail(f"List snapshots failed: {stderr}")

        # Create snapshot
        print(f"\n📌 Testing: Create snapshot")
        snapshot_name = f"test_snapshot_{int(time.time())}"
        cmd = ["./koala", "rollback", "create", snapshot_name]
        success, stdout, stderr = self.run_command(cmd)
        if success:
            self.print_test("Create snapshot", "PASS")
            result.add_pass()
        else:
            self.print_test("Create snapshot", "FAIL")
            result.add_fail(f"Create snapshot failed: {stderr}")

        result.end_time = time.time()
        return result

    async def test_dashboard(self) -> TestResult:
        """Test dashboard functionality"""
        result = TestResult("Dashboard")
        result.start_time = time.time()

        self.print_header("Testing Dashboard")

        print("⚠️  Dashboard test will launch browser and Electron app")
        print("You'll need to manually close them after testing")

        if self.interactive:
            confirm = input(f"\n{Colors.WARNING}Launch dashboard? (y/n): {Colors.ENDC}")
            if confirm.lower() != 'y':
                self.print_test("Dashboard test", "SKIP")
                result.add_skip()
                result.end_time = time.time()
                return result

        print(f"\n📌 Launching dashboard...")
        print("Check your browser and look for the Electron app")
        print("Press Ctrl+C in the dashboard terminal to stop it")

        # Note: Dashboard runs indefinitely, so we just check if it launches
        cmd = ["timeout", "5", "./koala", "dashboard"]
        success, stdout, stderr = self.run_command(cmd, timeout=10)

        # Success here means it started (will timeout after 5 seconds)
        if "Launching" in stdout or "Dashboard" in stdout:
            self.print_test("Dashboard launch", "PASS")
            result.add_pass()
        else:
            self.print_test("Dashboard launch", "FAIL")
            result.add_fail("Dashboard failed to launch")

        result.end_time = time.time()
        return result

    def generate_report(self, results: List[TestResult]):
        """Generate final test report"""
        self.print_header("Test Report")

        total_passed = sum(r.passed for r in results)
        total_failed = sum(r.failed for r in results)
        total_skipped = sum(r.skipped for r in results)
        total_tests = total_passed + total_failed + total_skipped

        print(f"{Colors.BOLD}Test Summary:{Colors.ENDC}")
        print(f"  Total Tests: {total_tests}")
        print(f"  {Colors.GREEN}Passed: {total_passed}{Colors.ENDC}")
        print(f"  {Colors.FAIL}Failed: {total_failed}{Colors.ENDC}")
        print(f"  {Colors.WARNING}Skipped: {total_skipped}{Colors.ENDC}")

        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"  Success Rate: {success_rate:.1f}%")

        print(f"\n{Colors.BOLD}Test Categories:{Colors.ENDC}")
        for result in results:
            duration = result.end_time - result.start_time if result.end_time else 0
            status_color = Colors.GREEN if result.failed == 0 else Colors.FAIL
            print(f"  {status_color}{result.name}:{Colors.ENDC}")
            print(f"    Passed: {result.passed}, Failed: {result.failed}, Skipped: {result.skipped}")
            print(f"    Duration: {duration:.2f}s")
            if result.errors:
                print(f"    Errors:")
                for error in result.errors[:3]:  # Show first 3 errors
                    print(f"      - {error[:100]}")

        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "skipped": total_skipped,
                "success_rate": success_rate if total_tests > 0 else 0
            },
            "categories": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "failed": r.failed,
                    "skipped": r.skipped,
                    "errors": r.errors
                }
                for r in results
            ]
        }

        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Report saved to: {report_file}")

    async def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print("="*80)
        print("🐨 KOALA'S FORGE - COMPREHENSIVE TEST SUITE")
        print("="*80)
        print(f"{Colors.ENDC}")

        print("\nThis test suite will walk you through all features of Koala's Forge")
        print("It will test installation, management, advanced features, and more.")
        print(f"\n{Colors.WARNING}⚠️  Some tests may modify your system (install/uninstall packages){Colors.ENDC}")

        if self.interactive:
            confirm = input(f"\n{Colors.CYAN}Run in interactive mode? (y/n): {Colors.ENDC}")
            self.interactive = confirm.lower() == 'y'

            verbose = input(f"{Colors.CYAN}Show verbose output? (y/n): {Colors.ENDC}")
            self.verbose = verbose.lower() == 'y'

        self.wait_for_input("\nReady to begin testing? Press Enter...")

        results = []

        # Run test suites
        test_suites = [
            ("Basic Commands", self.test_basic_commands),
            ("Package Management", self.test_package_management),
            ("Advanced Features", self.test_advanced_features),
            ("History & Privacy", self.test_history_and_privacy),
            ("Import/Export", self.test_import_export),
            ("Rollback System", self.test_rollback_system),
            ("Self-Test", self.test_self_test),
            ("Dashboard", self.test_dashboard),
        ]

        for name, test_func in test_suites:
            if self.interactive:
                confirm = input(f"\n{Colors.CYAN}Run {name} tests? (y/n/q): {Colors.ENDC}")
                if confirm.lower() == 'q':
                    break
                if confirm.lower() != 'y':
                    continue

            try:
                result = await test_func()
                results.append(result)
            except Exception as e:
                print(f"{Colors.FAIL}Test suite {name} failed: {e}{Colors.ENDC}")
                error_result = TestResult(name)
                error_result.add_fail(str(e))
                results.append(error_result)

        # Generate report
        self.generate_report(results)

        print(f"\n{Colors.GREEN}{Colors.BOLD}✨ Testing Complete!{Colors.ENDC}")
        print("\nThank you for testing Koala's Forge!")
        print("Please report any issues to: https://github.com/mykolas-perevicius/koalas-forge/issues")


async def main():
    """Main entry point"""
    suite = KoalaTestSuite()

    # Check if koala exists
    if not os.path.exists("./koala"):
        print(f"{Colors.FAIL}Error: ./koala not found!{Colors.ENDC}")
        print("Please run this test from the Koala's Forge directory")
        sys.exit(1)

    try:
        await suite.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Testing interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Test suite error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())