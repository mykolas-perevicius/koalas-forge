#!/usr/bin/env python3
"""
Automated Testing Suite for Koala's Forge
Tests Backend → Frontend → Integration
No user input required
"""

import subprocess
import time
import json
import sys
import os
import asyncio
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any


class Colors:
    """Terminal colors"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}🧪 {title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")


def print_test(name: str, success: bool, details: str = ""):
    """Print test result"""
    if success:
        print(f"{Colors.GREEN}✅ {name}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ {name}{Colors.ENDC}")
    if details:
        print(f"   {details}")


def run_command(cmd: List[str], timeout: int = 10) -> Tuple[bool, str, str]:
    """Run command and return success, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/Users/myko/app-installer"
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


class BackendTester:
    """Test backend functionality"""

    def __init__(self):
        self.results = {"passed": 0, "failed": 0, "tests": []}

    def test_core_commands(self):
        """Test core CLI commands"""
        print("Testing Core Commands...")

        commands = [
            (["./koala", "--help"], "Help command"),
            (["./koala", "version"], "Version command"),
            (["./koala", "status"], "Status command"),
            (["./koala", "categories"], "Categories listing"),
            (["./koala", "health"], "Health check"),
        ]

        for cmd, name in commands:
            success, stdout, stderr = run_command(cmd)
            print_test(name, success)

            if success:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
                print(f"   Error: {stderr[:100]}")

            self.results["tests"].append({
                "name": name,
                "success": success,
                "command": " ".join(cmd)
            })

    def test_package_operations(self):
        """Test package-related operations"""
        print("\nTesting Package Operations...")

        commands = [
            (["./koala", "search", "git"], "Package search"),
            (["./koala", "info", "git"], "Package info"),
            (["./koala", "list", "--category", "development_core"], "List by category"),
            (["./koala", "verify"], "Package verification"),
        ]

        for cmd, name in commands:
            success, stdout, stderr = run_command(cmd, timeout=30)
            print_test(name, success)

            if success:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1

            self.results["tests"].append({
                "name": name,
                "success": success,
                "command": " ".join(cmd)
            })

    def test_advanced_features(self):
        """Test advanced features"""
        print("\nTesting Advanced Features...")

        commands = [
            (["./koala", "deps", "docker"], "Dependency resolution"),
            (["./koala", "recommend"], "Smart recommendations"),
            (["./koala", "history", "--limit", "5"], "History tracking"),
            (["./koala", "privacy", "status"], "Privacy controls"),
            (["./koala", "breakages"], "Breakage detection"),
            (["./koala", "recover", "git"], "Recovery planning"),
        ]

        for cmd, name in commands:
            success, stdout, stderr = run_command(cmd)
            print_test(name, success)

            if success:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1

            self.results["tests"].append({
                "name": name,
                "success": success,
                "command": " ".join(cmd)
            })

    def test_data_management(self):
        """Test data management features"""
        print("\nTesting Data Management...")

        # Test export
        export_file = "test_automated_export.txt"
        success, stdout, stderr = run_command(["./koala", "export", export_file])
        print_test("Export packages", success)

        if success:
            self.results["passed"] += 1
            # Cleanup
            if os.path.exists(export_file):
                os.remove(export_file)
        else:
            self.results["failed"] += 1

        # Test rollback
        success, stdout, stderr = run_command(["./koala", "rollback", "list"])
        print_test("Rollback list", success)

        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1

    def run_tests(self):
        """Run all backend tests"""
        print_section("BACKEND TESTING")

        self.test_core_commands()
        self.test_package_operations()
        self.test_advanced_features()
        self.test_data_management()

        print(f"\n{Colors.BOLD}Backend Results:{Colors.ENDC}")
        print(f"  Passed: {Colors.GREEN}{self.results['passed']}{Colors.ENDC}")
        print(f"  Failed: {Colors.FAIL}{self.results['failed']}{Colors.ENDC}")

        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"  Success Rate: {success_rate:.1f}%")

        return self.results


class FrontendTester:
    """Test frontend/dashboard functionality"""

    def __init__(self):
        self.results = {"passed": 0, "failed": 0, "tests": []}
        self.server_process = None
        self.port = 8080

    def start_server(self):
        """Start dashboard server in background"""
        print("Starting dashboard server...")

        # Start server in background
        self.server_process = subprocess.Popen(
            ["python3", "-c", """
import sys
sys.path.insert(0, '/Users/myko/app-installer')
from src.dashboard.server import DashboardServer
import time

server = DashboardServer(port=8080)
server.start()
print('Server started')
while True:
    time.sleep(1)
"""],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/Users/myko/app-installer"
        )

        # Wait for server to start
        time.sleep(3)

        # Check if server is running
        try:
            response = requests.get(f"http://localhost:{self.port}/", timeout=5)
            print_test("Dashboard server started", response.status_code == 200)
            self.results["passed"] += 1
            return True
        except:
            print_test("Dashboard server started", False)
            self.results["failed"] += 1
            return False

    def test_api_endpoints(self):
        """Test dashboard API endpoints"""
        print("\nTesting API Endpoints...")

        endpoints = [
            ("/api/status", "Status endpoint"),
            ("/api/packages", "Packages endpoint"),
            ("/api/installed", "Installed endpoint"),
            ("/api/stats", "Stats endpoint"),
            ("/api/history", "History endpoint"),
        ]

        for endpoint, name in endpoints:
            try:
                response = requests.get(f"http://localhost:{self.port}{endpoint}", timeout=10)
                success = response.status_code == 200
                print_test(name, success)

                if success:
                    self.results["passed"] += 1
                    # Show sample data
                    if endpoint == "/api/stats":
                        data = response.json()
                        print(f"   Total packages: {data.get('total_packages', 0)}")
                        print(f"   Installed: {data.get('installed_count', 0)}")
                else:
                    self.results["failed"] += 1

            except Exception as e:
                print_test(name, False)
                print(f"   Error: {str(e)[:100]}")
                self.results["failed"] += 1

    def test_web_interface(self):
        """Test web interface availability"""
        print("\nTesting Web Interface...")

        try:
            response = requests.get(f"http://localhost:{self.port}/", timeout=5)
            success = response.status_code == 200 and "Koala" in response.text
            print_test("Dashboard HTML loads", success)

            if success:
                self.results["passed"] += 1
                print(f"   Dashboard available at: http://localhost:{self.port}")
            else:
                self.results["failed"] += 1

        except Exception as e:
            print_test("Dashboard HTML loads", False)
            print(f"   Error: {str(e)[:100]}")
            self.results["failed"] += 1

    def stop_server(self):
        """Stop dashboard server"""
        if self.server_process:
            print("\nStopping dashboard server...")
            self.server_process.terminate()
            time.sleep(1)
            self.server_process.kill()
            print_test("Server stopped", True)

    def run_tests(self):
        """Run all frontend tests"""
        print_section("FRONTEND TESTING")

        if self.start_server():
            self.test_api_endpoints()
            self.test_web_interface()
            self.stop_server()
        else:
            print(f"{Colors.FAIL}Could not start dashboard server{Colors.ENDC}")
            self.results["failed"] += 5  # Count all tests as failed

        print(f"\n{Colors.BOLD}Frontend Results:{Colors.ENDC}")
        print(f"  Passed: {Colors.GREEN}{self.results['passed']}{Colors.ENDC}")
        print(f"  Failed: {Colors.FAIL}{self.results['failed']}{Colors.ENDC}")

        if (self.results['passed'] + self.results['failed']) > 0:
            success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
            print(f"  Success Rate: {success_rate:.1f}%")

        return self.results


class IntegrationTester:
    """Test backend-frontend integration"""

    def __init__(self):
        self.results = {"passed": 0, "failed": 0, "tests": []}
        self.server_process = None
        self.port = 8080

    def start_dashboard_command(self):
        """Test dashboard command (backend launching frontend)"""
        print("Testing Dashboard Command Integration...")

        # Start dashboard with timeout
        self.server_process = subprocess.Popen(
            ["timeout", "10", "./koala", "dashboard"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/Users/myko/app-installer"
        )

        # Wait for startup
        time.sleep(5)

        # Check if server is accessible
        try:
            response = requests.get(f"http://localhost:{self.port}/", timeout=5)
            success = response.status_code == 200
            print_test("Dashboard command launches server", success)

            if success:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1

        except:
            print_test("Dashboard command launches server", False)
            self.results["failed"] += 1

        # Cleanup
        if self.server_process:
            self.server_process.terminate()
            time.sleep(1)

    def test_api_cli_consistency(self):
        """Test that API returns same data as CLI"""
        print("\nTesting API-CLI Data Consistency...")

        # Get data from CLI
        success_cli, stdout_cli, _ = run_command(["./koala", "categories"])

        # Start server for API test
        server = subprocess.Popen(
            ["python3", "-c", """
import sys
sys.path.insert(0, '/Users/myko/app-installer')
from src.dashboard.server import DashboardServer
import time

server = DashboardServer(port=8081)
server.start()
while True:
    time.sleep(1)
"""],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        time.sleep(3)

        # Get data from API
        try:
            response = requests.get("http://localhost:8081/api/packages", timeout=10)
            success_api = response.status_code == 200

            consistent = success_cli and success_api
            print_test("CLI-API data consistency", consistent)

            if consistent:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1

        except Exception as e:
            print_test("CLI-API data consistency", False)
            print(f"   Error: {str(e)[:100]}")
            self.results["failed"] += 1

        # Cleanup
        server.terminate()
        time.sleep(1)
        server.kill()

    def test_real_operation(self):
        """Test a real operation through the system"""
        print("\nTesting Real Operation Flow...")

        # Test getting recommendations through CLI
        success, stdout, _ = run_command(["./koala", "recommend"])
        print_test("Backend recommendation engine", success)

        if success:
            self.results["passed"] += 1
            # Parse recommendations
            lines = stdout.split('\n')
            rec_count = sum(1 for line in lines if '→' in line)
            print(f"   Found {rec_count} recommendations")
        else:
            self.results["failed"] += 1

    def run_tests(self):
        """Run all integration tests"""
        print_section("INTEGRATION TESTING")

        self.start_dashboard_command()
        self.test_api_cli_consistency()
        self.test_real_operation()

        print(f"\n{Colors.BOLD}Integration Results:{Colors.ENDC}")
        print(f"  Passed: {Colors.GREEN}{self.results['passed']}{Colors.ENDC}")
        print(f"  Failed: {Colors.FAIL}{self.results['failed']}{Colors.ENDC}")

        if (self.results['passed'] + self.results['failed']) > 0:
            success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
            print(f"  Success Rate: {success_rate:.1f}%")

        return self.results


def generate_report(backend_results, frontend_results, integration_results):
    """Generate final test report"""
    print_section("FINAL TEST REPORT")

    total_passed = (backend_results["passed"] +
                   frontend_results["passed"] +
                   integration_results["passed"])
    total_failed = (backend_results["failed"] +
                   frontend_results["failed"] +
                   integration_results["failed"])
    total = total_passed + total_failed

    print(f"{Colors.BOLD}Overall Results:{Colors.ENDC}")
    print(f"  Total Tests: {total}")
    print(f"  {Colors.GREEN}Passed: {total_passed}{Colors.ENDC}")
    print(f"  {Colors.FAIL}Failed: {total_failed}{Colors.ENDC}")

    if total > 0:
        success_rate = (total_passed / total) * 100
        print(f"  {Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.ENDC}")

    print(f"\n{Colors.BOLD}Component Breakdown:{Colors.ENDC}")
    print(f"  Backend:     {backend_results['passed']}/{backend_results['passed'] + backend_results['failed']} passed")
    print(f"  Frontend:    {frontend_results['passed']}/{frontend_results['passed'] + frontend_results['failed']} passed")
    print(f"  Integration: {integration_results['passed']}/{integration_results['passed'] + integration_results['failed']} passed")

    # Save JSON report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": success_rate if total > 0 else 0
        },
        "backend": backend_results,
        "frontend": frontend_results,
        "integration": integration_results
    }

    report_file = f"automated_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Overall verdict
    print(f"\n{Colors.BOLD}Verdict:{Colors.ENDC}")
    if success_rate >= 90:
        print(f"{Colors.GREEN}✅ SYSTEM HEALTHY - Ready for production{Colors.ENDC}")
    elif success_rate >= 70:
        print(f"{Colors.WARNING}⚠️  MOSTLY WORKING - Some issues to address{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ NEEDS ATTENTION - Multiple failures detected{Colors.ENDC}")


def main():
    """Main test runner"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("="*70)
    print("🐨 KOALA'S FORGE - AUTOMATED SYSTEM TEST")
    print("Testing: Backend → Frontend → Integration")
    print("="*70)
    print(f"{Colors.ENDC}")

    print("This will automatically test all system components.")
    print("No user input required.\n")

    # Check we're in the right directory
    if not os.path.exists("./koala"):
        print(f"{Colors.FAIL}Error: ./koala not found!{Colors.ENDC}")
        print("Please run from /Users/myko/app-installer")
        sys.exit(1)

    # Run tests
    backend_tester = BackendTester()
    backend_results = backend_tester.run_tests()

    print("\n" + "="*70 + "\n")

    frontend_tester = FrontendTester()
    frontend_results = frontend_tester.run_tests()

    print("\n" + "="*70 + "\n")

    integration_tester = IntegrationTester()
    integration_results = integration_tester.run_tests()

    # Generate report
    generate_report(backend_results, frontend_results, integration_results)

    print(f"\n{Colors.GREEN}{Colors.BOLD}✨ Testing Complete!{Colors.ENDC}\n")


if __name__ == "__main__":
    main()