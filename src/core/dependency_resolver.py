#!/usr/bin/env python3
"""
Intelligent Dependency Resolution System for Koala's Forge
Handles package dependencies, conflicts, and auto-recovery
"""

import asyncio
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any
from enum import Enum
from datetime import datetime
import networkx as nx
import subprocess
import yaml


class DependencyType(Enum):
    """Types of dependencies"""
    REQUIRED = "required"       # Must be installed
    RECOMMENDED = "recommended"  # Should be installed
    OPTIONAL = "optional"        # Can be installed
    CONFLICTS = "conflicts"      # Cannot coexist
    REPLACES = "replaces"        # Can replace another package


@dataclass
class PackageRelation:
    """Represents a relationship between packages"""
    package: str
    relation_type: DependencyType
    version_constraint: Optional[str] = None
    reason: Optional[str] = None


@dataclass
class Package:
    """Enhanced package with dependency information"""
    name: str
    version: Optional[str] = None
    dependencies: List[PackageRelation] = field(default_factory=list)
    installed: bool = False
    available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolutionResult:
    """Result of dependency resolution"""
    install_order: List[str]
    conflicts: List[Tuple[str, str]]
    missing: List[str]
    optional: List[str]
    replacements: Dict[str, str]
    dependency_graph: Optional[nx.DiGraph] = None


@dataclass
class RecoveryPlan:
    """Plan for recovering from package breakage"""
    broken_package: str
    root_cause: Optional[str]
    steps: List[str]
    commands: List[str]
    confidence: float
    estimated_time: int  # seconds


class DependencyResolver:
    """
    Intelligent dependency resolver with conflict detection
    and auto-recovery capabilities
    """

    def __init__(self, apps_file: str = None):
        # Use enhanced file if it exists, otherwise fall back to regular apps.yaml
        if apps_file is None:
            if os.path.exists('apps_enhanced.yaml'):
                self.apps_file = 'apps_enhanced.yaml'
            else:
                self.apps_file = 'apps.yaml'
        else:
            self.apps_file = apps_file
        self.packages: Dict[str, Package] = {}
        self.dependency_graph = nx.DiGraph()
        self.conflict_graph = nx.Graph()
        self.load_package_data()

    def load_package_data(self):
        """Load package data with dependency information"""
        if not os.path.exists(self.apps_file):
            return

        with open(self.apps_file, 'r') as f:
            data = yaml.safe_load(f)

        # Handle both formats (apps.yaml with nested 'apps' key and direct format)
        if 'apps' in data:
            apps = data['apps']
        else:
            apps = data

        for category, packages in apps.items():
            if not packages:
                continue

            # Handle list format (original apps.yaml)
            if isinstance(packages, list):
                for pkg_item in packages:
                    if not isinstance(pkg_item, dict):
                        continue
                    pkg_name = pkg_item.get('package', pkg_item.get('name', ''))
                    if pkg_name:
                        package = Package(
                            name=pkg_name,
                            version=pkg_item.get('version'),
                            installed=self.check_if_installed(pkg_name),
                            metadata=pkg_item
                        )
                        self.packages[pkg_name] = package

            # Handle dict format (apps_enhanced.yaml)
            elif isinstance(packages, dict):
                for pkg_name, pkg_info in packages.items():
                    if not isinstance(pkg_info, dict):
                        continue
                    package = Package(
                        name=pkg_name,
                        version=pkg_info.get('version'),
                        installed=self.check_if_installed(pkg_name),
                        metadata=pkg_info
                    )

                    # Parse dependencies
                    if 'dependencies' in pkg_info:
                        for dep in pkg_info['dependencies']:
                            if isinstance(dep, str):
                                package.dependencies.append(
                                    PackageRelation(dep, DependencyType.REQUIRED)
                                )
                            elif isinstance(dep, dict):
                                package.dependencies.append(
                                    PackageRelation(
                                        dep.get('name'),
                                        DependencyType[dep.get('type', 'REQUIRED').upper()],
                                        dep.get('version'),
                                        dep.get('reason')
                                    )
                                )

                    self.packages[pkg_name] = package

    def check_if_installed(self, package: str) -> bool:
        """Check if package is installed"""
        # Check brew
        try:
            result = subprocess.run(
                ['brew', 'list', package],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return True
        except:
            pass

        # Check brew cask
        try:
            result = subprocess.run(
                ['brew', 'list', '--cask', package],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return True
        except:
            pass

        return False

    def build_dependency_graph(self, packages: List[str]) -> nx.DiGraph:
        """Build dependency graph for given packages"""
        graph = nx.DiGraph()
        visited = set()

        def add_dependencies(pkg_name: str, depth: int = 0):
            if pkg_name in visited or depth > 10:  # Prevent infinite recursion
                return
            visited.add(pkg_name)

            if pkg_name not in self.packages:
                return

            package = self.packages[pkg_name]
            graph.add_node(pkg_name, package=package)

            for relation in package.dependencies:
                if relation.relation_type in [DependencyType.REQUIRED, DependencyType.RECOMMENDED]:
                    graph.add_edge(
                        relation.package,
                        pkg_name,
                        type=relation.relation_type.value,
                        version=relation.version_constraint
                    )
                    add_dependencies(relation.package, depth + 1)
                elif relation.relation_type == DependencyType.CONFLICTS:
                    self.conflict_graph.add_edge(pkg_name, relation.package)

        for pkg in packages:
            add_dependencies(pkg)

        return graph

    async def resolve_dependencies(self, packages: List[str]) -> ResolutionResult:
        """Resolve dependencies for a list of packages"""
        # Build dependency graph
        graph = self.build_dependency_graph(packages)

        # Detect conflicts
        conflicts = []
        for pkg1, pkg2 in self.conflict_graph.edges():
            if pkg1 in graph.nodes() and pkg2 in graph.nodes():
                conflicts.append((pkg1, pkg2))

        # Topological sort for install order
        install_order = []
        if nx.is_directed_acyclic_graph(graph):
            install_order = list(nx.topological_sort(graph))
        else:
            # Handle cycles
            cycles = list(nx.simple_cycles(graph))
            if cycles:
                print(f"⚠️  Dependency cycles detected: {cycles}")
            # Use approximation
            install_order = list(graph.nodes())

        # Find missing packages
        missing = []
        for pkg in install_order:
            if pkg not in self.packages or not self.packages[pkg].available:
                missing.append(pkg)

        # Find optional dependencies
        optional = []
        for pkg in graph.nodes():
            if pkg in self.packages:
                for rel in self.packages[pkg].dependencies:
                    if rel.relation_type == DependencyType.OPTIONAL:
                        optional.append(rel.package)

        # Find replacements
        replacements = {}
        for pkg in graph.nodes():
            if pkg in self.packages:
                for rel in self.packages[pkg].dependencies:
                    if rel.relation_type == DependencyType.REPLACES:
                        replacements[rel.package] = pkg

        return ResolutionResult(
            install_order=install_order,
            conflicts=conflicts,
            missing=missing,
            optional=optional,
            replacements=replacements,
            dependency_graph=graph
        )

    async def detect_conflicts(self, package: str, installed: List[str]) -> List[str]:
        """Detect conflicts between package and installed packages"""
        conflicts = []

        if package not in self.packages:
            return conflicts

        pkg = self.packages[package]
        for relation in pkg.dependencies:
            if relation.relation_type == DependencyType.CONFLICTS:
                if relation.package in installed:
                    conflicts.append(relation.package)

        # Check reverse conflicts
        for installed_pkg in installed:
            if installed_pkg in self.packages:
                for rel in self.packages[installed_pkg].dependencies:
                    if rel.relation_type == DependencyType.CONFLICTS and rel.package == package:
                        conflicts.append(installed_pkg)

        return conflicts

    async def create_recovery_plan(self, broken_package: str, error_log: Optional[str] = None) -> RecoveryPlan:
        """Create recovery plan for broken package"""
        steps = []
        commands = []
        confidence = 0.0

        # Analyze the package
        if broken_package in self.packages:
            pkg = self.packages[broken_package]

            # Check missing dependencies
            for rel in pkg.dependencies:
                if rel.relation_type == DependencyType.REQUIRED:
                    if not self.check_if_installed(rel.package):
                        steps.append(f"Install missing dependency: {rel.package}")
                        commands.append(f"brew install {rel.package}")
                        confidence += 0.3

            # Check for conflicts
            installed = [p for p in self.packages if self.packages[p].installed]
            conflicts = await self.detect_conflicts(broken_package, installed)

            if conflicts:
                for conflict in conflicts:
                    steps.append(f"Remove conflicting package: {conflict}")
                    commands.append(f"brew uninstall {conflict}")
                    confidence += 0.2

            # Try reinstall
            if not steps:
                steps.append(f"Reinstall {broken_package}")
                commands.append(f"brew reinstall {broken_package}")
                confidence = 0.5

        # Parse error log for clues
        if error_log:
            if "permission denied" in error_log.lower():
                steps.insert(0, "Fix permissions")
                commands.insert(0, "sudo chown -R $(whoami) /usr/local")
                confidence += 0.2
            elif "not found" in error_log.lower():
                steps.insert(0, "Update PATH")
                commands.insert(0, "export PATH=/usr/local/bin:$PATH")
                confidence += 0.1

        confidence = min(confidence, 0.95)  # Never be 100% sure
        estimated_time = len(commands) * 30  # 30 seconds per command

        return RecoveryPlan(
            broken_package=broken_package,
            root_cause="Dependency or conflict issue" if steps else "Unknown",
            steps=steps,
            commands=commands,
            confidence=confidence,
            estimated_time=estimated_time
        )

    def visualize_dependencies(self, packages: List[str]) -> str:
        """Generate ASCII visualization of dependencies"""
        graph = self.build_dependency_graph(packages)

        if not graph.nodes():
            return "No dependencies found"

        lines = []
        lines.append("Dependency Graph:")
        lines.append("=" * 50)

        # Show each package and its dependencies
        for node in graph.nodes():
            deps = list(graph.predecessors(node))
            if deps:
                lines.append(f"📦 {node}")
                for i, dep in enumerate(deps):
                    is_last = i == len(deps) - 1
                    prefix = "  └─" if is_last else "  ├─"
                    edge_data = graph.get_edge_data(dep, node)
                    dep_type = edge_data.get('type', 'required') if edge_data else 'required'
                    symbol = "🔴" if dep_type == 'required' else "🟡"
                    lines.append(f"{prefix} {symbol} {dep}")
            else:
                lines.append(f"📦 {node} (no dependencies)")

        return "\n".join(lines)

    async def get_smart_recommendations(self, installed: List[str]) -> List[Tuple[str, str, float]]:
        """Get smart package recommendations based on what's installed"""
        recommendations = []
        scores = {}

        # Build co-occurrence matrix
        for pkg in installed:
            if pkg not in self.packages:
                continue

            # Recommend dependencies
            for rel in self.packages[pkg].dependencies:
                if rel.relation_type in [DependencyType.RECOMMENDED, DependencyType.OPTIONAL]:
                    if not self.check_if_installed(rel.package):
                        reason = rel.reason or f"Recommended for {pkg}"
                        if rel.package not in scores:
                            scores[rel.package] = []
                        scores[rel.package].append((reason, 0.5 if rel.relation_type == DependencyType.OPTIONAL else 0.8))

        # Look for common patterns
        dev_tools = ['git', 'docker', 'nodejs', 'python']
        if any(tool in installed for tool in dev_tools[:2]):
            for tool in dev_tools:
                if tool not in installed and tool in self.packages:
                    if tool not in scores:
                        scores[tool] = []
                    scores[tool].append(("Common development tool", 0.6))

        # Calculate final scores
        for pkg, reasons in scores.items():
            total_score = min(sum(score for _, score in reasons), 1.0)
            main_reason = max(reasons, key=lambda x: x[1])[0]
            recommendations.append((pkg, main_reason, total_score))

        # Sort by score
        recommendations.sort(key=lambda x: x[2], reverse=True)

        return recommendations[:10]  # Top 10


def get_dependency_resolver():
    """Get singleton instance of dependency resolver"""
    if not hasattr(get_dependency_resolver, '_instance'):
        get_dependency_resolver._instance = DependencyResolver()
    return get_dependency_resolver._instance


if __name__ == "__main__":
    # Test the resolver
    async def test():
        resolver = get_dependency_resolver()

        # Test dependency resolution
        result = await resolver.resolve_dependencies(['docker', 'nodejs'])
        print(f"Install order: {result.install_order}")
        print(f"Conflicts: {result.conflicts}")

        # Test visualization
        viz = resolver.visualize_dependencies(['docker'])
        print(viz)

        # Test recovery plan
        plan = await resolver.create_recovery_plan('docker')
        print(f"Recovery plan: {plan.steps}")

    asyncio.run(test())