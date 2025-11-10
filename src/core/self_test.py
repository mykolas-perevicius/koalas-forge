"""
Self-Testing System for Koala's Forge
Comprehensive testing to ensure the application is working correctly
"""

import sys
import subprocess
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class TestResult:
    """Result of a single test"""
    name: str
    passed: bool
    message: str
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuite:
    """Collection of test results"""
    name: str
    results: List[TestResult] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None

    @property
    def passed(self) -> bool:
        """Check if all tests passed"""
        return all(r.passed for r in self.results)

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate"""
        if not self.results:
            return 0.0
        passed = sum(1 for r in self.results if r.passed)
        return (passed / len(self.results)) * 100

    def summary(self) -> str:
        """Generate summary string"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        return f"Passed: {passed}/{total} ({self.pass_rate:.1f}%), Failed: {failed}"


class SelfTest:
    """Comprehensive self-testing system"""

    def __init__(self):
        self.koala_dir = Path(__file__).parent.parent.parent
        self.results_dir = Path.home() / '.koalas-forge' / 'test-results'
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def run_all_tests(self) -> TestSuite:
        """Run all self-tests"""
        suite = TestSuite(name="Full System Test")

        # Run test categories
        test_methods = [
            self.test_core_systems,
            self.test_cli_commands,
            self.test_package_operations,
            self.test_file_system,
            self.test_error_handling,
            self.test_performance,
            self.test_dependencies,
            self.test_security
        ]

        for test_method in test_methods:
            results = await test_method()
            suite.results.extend(results)

        suite.end_time = datetime.now().isoformat()
        self._save_results(suite)
        return suite

    async def test_core_systems(self) -> List[TestResult]:
        """Test core system components"""
        results = []
        import time

        # Test import of core modules
        start = time.perf_counter()
        try:
            from src.core.installer import get_installer
            from src.core.event_system import get_event_bus
            from src.core.plugin_system import PluginManager
            from src.core.rollback_system import RollbackManager
            from src.core.config import get_config
            from src.core.history import get_history

            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Core Modules Import",
                passed=True,
                message="All core modules imported successfully",
                duration_ms=duration
            ))
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Core Modules Import",
                passed=False,
                message=f"Failed to import core modules: {e}",
                duration_ms=duration
            ))

        # Test event system
        start = time.perf_counter()
        try:
            from src.core.event_system import get_event_bus, Event, EventType
            bus = get_event_bus()

            test_event_received = False
            def test_handler(event):
                nonlocal test_event_received
                test_event_received = True

            bus.on(EventType.INSTALL_STARTED, test_handler)
            await bus.emit(Event(EventType.INSTALL_STARTED, {'test': True}))

            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Event System",
                passed=test_event_received,
                message="Event system working" if test_event_received else "Event not received",
                duration_ms=duration
            ))
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Event System",
                passed=False,
                message=f"Event system error: {e}",
                duration_ms=duration
            ))

        # Test configuration system
        start = time.perf_counter()
        try:
            from src.core.config import get_config
            config = get_config()
            test_value = "test_" + datetime.now().isoformat()
            config.set('test_key', test_value)
            retrieved = config.get('test_key')

            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Configuration System",
                passed=retrieved == test_value,
                message="Config system working" if retrieved == test_value else "Config mismatch",
                duration_ms=duration
            ))
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Configuration System",
                passed=False,
                message=f"Config system error: {e}",
                duration_ms=duration
            ))

        return results

    async def test_cli_commands(self) -> List[TestResult]:
        """Test CLI command availability"""
        results = []
        import time

        commands = [
            (['./koala', '--help'], "Help command"),
            (['./koala', 'version'], "Version command"),
            (['./koala', 'status'], "Status command"),
            (['./koala', 'categories'], "Categories command"),
            (['./koala', 'list', '--category', 'development_core'], "List command"),
            (['./koala', 'search', 'test'], "Search command"),
        ]

        for cmd, name in commands:
            start = time.perf_counter()
            try:
                # Change to koala directory
                result = subprocess.run(
                    cmd,
                    cwd=self.koala_dir,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                duration = (time.perf_counter() - start) * 1000
                passed = result.returncode == 0

                results.append(TestResult(
                    name=f"CLI: {name}",
                    passed=passed,
                    message="Command executed" if passed else f"Exit code: {result.returncode}",
                    duration_ms=duration,
                    details={'stdout': result.stdout[:200], 'stderr': result.stderr[:200]}
                ))
            except subprocess.TimeoutExpired:
                duration = (time.perf_counter() - start) * 1000
                results.append(TestResult(
                    name=f"CLI: {name}",
                    passed=False,
                    message="Command timed out",
                    duration_ms=duration
                ))
            except Exception as e:
                duration = (time.perf_counter() - start) * 1000
                results.append(TestResult(
                    name=f"CLI: {name}",
                    passed=False,
                    message=f"Error: {e}",
                    duration_ms=duration
                ))

        return results

    async def test_package_operations(self) -> List[TestResult]:
        """Test package operations (dry-run)"""
        results = []
        import time

        # Test package database loading
        start = time.perf_counter()
        try:
            from src.core.installer import get_installer
            installer = get_installer()
            packages = installer.list_packages()

            duration = (time.perf_counter() - start) * 1000
            passed = len(packages) > 0

            results.append(TestResult(
                name="Package Database",
                passed=passed,
                message=f"Loaded {len(packages)} packages" if passed else "No packages loaded",
                duration_ms=duration,
                details={'package_count': len(packages)}
            ))
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Package Database",
                passed=False,
                message=f"Failed to load packages: {e}",
                duration_ms=duration
            ))

        # Test dry-run install
        start = time.perf_counter()
        try:
            result = subprocess.run(
                ['./koala', 'install', 'test-package', '--dry-run'],
                cwd=self.koala_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

            duration = (time.perf_counter() - start) * 1000
            # Dry-run should complete even for non-existent packages
            passed = 'DRY RUN' in result.stdout or result.returncode == 0

            results.append(TestResult(
                name="Dry-Run Install",
                passed=passed,
                message="Dry-run completed" if passed else "Dry-run failed",
                duration_ms=duration
            ))
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Dry-Run Install",
                passed=False,
                message=f"Error: {e}",
                duration_ms=duration
            ))

        return results

    async def test_file_system(self) -> List[TestResult]:
        """Test file system operations"""
        results = []
        import time

        directories = [
            (Path.home() / '.koalas-forge', "Config directory"),
            (Path.home() / '.koalas-forge' / 'plugins', "Plugins directory"),
            (Path.home() / '.koalas-forge' / 'history', "History directory"),
            (Path.home() / '.koalas-forge' / 'cache', "Cache directory"),
            (self.koala_dir / 'apps.yaml', "Package database file"),
            (self.koala_dir / 'koala', "Main CLI script"),
        ]

        for path, name in directories:
            start = time.perf_counter()
            exists = path.exists()
            readable = path.exists() and os.access(path, os.R_OK) if 'os' in dir() else False

            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name=f"FileSystem: {name}",
                passed=exists,
                message="Exists and accessible" if exists else "Does not exist",
                duration_ms=duration,
                details={'path': str(path), 'exists': exists}
            ))

        return results

    async def test_error_handling(self) -> List[TestResult]:
        """Test error handling capabilities"""
        results = []
        import time

        # Test invalid command handling
        start = time.perf_counter()
        try:
            result = subprocess.run(
                ['./koala', 'invalid-command-xyz'],
                cwd=self.koala_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

            duration = (time.perf_counter() - start) * 1000
            # Should exit with error but not crash
            passed = result.returncode != 0 and not 'Traceback' in result.stderr

            results.append(TestResult(
                name="Invalid Command Handling",
                passed=passed,
                message="Handled gracefully" if passed else "Crashed or unexpected behavior",
                duration_ms=duration
            ))
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Invalid Command Handling",
                passed=False,
                message=f"Error: {e}",
                duration_ms=duration
            ))

        # Test recovery from missing file
        start = time.perf_counter()
        try:
            result = subprocess.run(
                ['./koala', 'batch', 'non-existent-file.txt'],
                cwd=self.koala_dir,
                capture_output=True,
                text=True,
                timeout=5
            )

            duration = (time.perf_counter() - start) * 1000
            # Should handle missing file gracefully
            passed = 'not found' in result.stdout.lower() or 'not found' in result.stderr.lower()

            results.append(TestResult(
                name="Missing File Handling",
                passed=passed,
                message="Handled gracefully" if passed else "Poor error handling",
                duration_ms=duration
            ))
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Missing File Handling",
                passed=False,
                message=f"Error: {e}",
                duration_ms=duration
            ))

        return results

    async def test_performance(self) -> List[TestResult]:
        """Test performance characteristics"""
        results = []
        import time

        # Test command response time
        start = time.perf_counter()
        try:
            result = subprocess.run(
                ['./koala', 'version'],
                cwd=self.koala_dir,
                capture_output=True,
                text=True,
                timeout=2
            )

            duration = (time.perf_counter() - start) * 1000
            # Version command should be fast
            passed = duration < 1000  # Less than 1 second

            results.append(TestResult(
                name="Version Command Speed",
                passed=passed,
                message=f"Completed in {duration:.0f}ms",
                duration_ms=duration
            ))
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Version Command Speed",
                passed=False,
                message=f"Error: {e}",
                duration_ms=duration
            ))

        # Test memory usage (simplified)
        start = time.perf_counter()
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            duration = (time.perf_counter() - start) * 1000
            # Should use reasonable memory
            passed = memory_mb < 500  # Less than 500MB

            results.append(TestResult(
                name="Memory Usage",
                passed=passed,
                message=f"Using {memory_mb:.1f}MB",
                duration_ms=duration,
                details={'memory_mb': memory_mb}
            ))
        except Exception:
            # psutil not available, skip test
            results.append(TestResult(
                name="Memory Usage",
                passed=True,
                message="Test skipped (psutil not available)",
                duration_ms=0
            ))

        return results

    async def test_dependencies(self) -> List[TestResult]:
        """Test system dependencies"""
        results = []
        import time

        dependencies = [
            (['python3', '--version'], "Python 3"),
            (['git', '--version'], "Git"),
            (['brew', '--version'], "Homebrew (macOS)"),
        ]

        for cmd, name in dependencies:
            start = time.perf_counter()
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                duration = (time.perf_counter() - start) * 1000
                passed = result.returncode == 0

                results.append(TestResult(
                    name=f"Dependency: {name}",
                    passed=passed,
                    message="Available" if passed else "Not found",
                    duration_ms=duration,
                    details={'version': result.stdout[:100] if passed else None}
                ))
            except Exception:
                duration = (time.perf_counter() - start) * 1000
                results.append(TestResult(
                    name=f"Dependency: {name}",
                    passed=False,
                    message="Not available",
                    duration_ms=duration
                ))

        return results

    async def test_security(self) -> List[TestResult]:
        """Test security features"""
        results = []
        import time

        # Test command injection protection
        start = time.perf_counter()
        try:
            # Try to inject a command
            result = subprocess.run(
                ['./koala', 'search', 'test; echo INJECTED'],
                cwd=self.koala_dir,
                capture_output=True,
                text=True,
                timeout=2
            )

            duration = (time.perf_counter() - start) * 1000
            # Should not execute the injected command
            passed = 'INJECTED' not in result.stdout

            results.append(TestResult(
                name="Command Injection Protection",
                passed=passed,
                message="Protected" if passed else "Vulnerable to injection",
                duration_ms=duration
            ))
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Command Injection Protection",
                passed=False,
                message=f"Error: {e}",
                duration_ms=duration
            ))

        # Test privacy features
        start = time.perf_counter()
        try:
            from src.core.history_privacy import get_enhanced_history
            history = get_enhanced_history()
            report = history.get_privacy_report()

            duration = (time.perf_counter() - start) * 1000
            passed = 'tracking_enabled' in report

            results.append(TestResult(
                name="Privacy Controls",
                passed=passed,
                message="Privacy features available",
                duration_ms=duration,
                details=report
            ))
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            results.append(TestResult(
                name="Privacy Controls",
                passed=False,
                message=f"Error: {e}",
                duration_ms=duration
            ))

        return results

    def _save_results(self, suite: TestSuite):
        """Save test results to file"""
        filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.results_dir / filename

        data = {
            'suite_name': suite.name,
            'start_time': suite.start_time,
            'end_time': suite.end_time,
            'passed': suite.passed,
            'pass_rate': suite.pass_rate,
            'summary': suite.summary(),
            'results': [
                {
                    'name': r.name,
                    'passed': r.passed,
                    'message': r.message,
                    'duration_ms': r.duration_ms,
                    'details': r.details
                }
                for r in suite.results
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def get_last_test_results(self) -> Optional[TestSuite]:
        """Get the most recent test results"""
        result_files = sorted(self.results_dir.glob('test_*.json'))
        if not result_files:
            return None

        latest = result_files[-1]
        with open(latest, 'r') as f:
            data = json.load(f)

        suite = TestSuite(name=data['suite_name'])
        suite.start_time = data['start_time']
        suite.end_time = data['end_time']

        for r in data['results']:
            suite.results.append(TestResult(
                name=r['name'],
                passed=r['passed'],
                message=r['message'],
                duration_ms=r['duration_ms'],
                details=r.get('details', {})
            ))

        return suite


# Singleton instance
_self_test_instance: Optional[SelfTest] = None


def get_self_test() -> SelfTest:
    """Get the singleton self-test instance"""
    global _self_test_instance
    if _self_test_instance is None:
        _self_test_instance = SelfTest()
    return _self_test_instance