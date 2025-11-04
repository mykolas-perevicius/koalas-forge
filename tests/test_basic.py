#!/usr/bin/env python3
"""
Basic tests for Koala's Forge
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_apps_yaml_exists():
    """Test that apps.yaml exists"""
    apps_yaml = Path(__file__).parent.parent / 'apps.yaml'
    assert apps_yaml.exists(), "apps.yaml should exist"


def test_apps_yaml_valid():
    """Test that apps.yaml is valid YAML"""
    import yaml
    apps_yaml = Path(__file__).parent.parent / 'apps.yaml'

    with open(apps_yaml, 'r') as f:
        data = yaml.safe_load(f)

    assert data is not None, "apps.yaml should not be empty"
    assert 'apps' in data, "apps.yaml should have 'apps' key"


def test_apps_have_required_fields():
    """Test that all apps have required fields"""
    import yaml
    apps_yaml = Path(__file__).parent.parent / 'apps.yaml'

    with open(apps_yaml, 'r') as f:
        data = yaml.safe_load(f)

    required_fields = ['name', 'package', 'platforms', 'install_type']

    for category, apps in data.get('apps', {}).items():
        for app in apps:
            for field in required_fields:
                assert field in app, f"App in {category} missing {field}: {app}"


def test_launch_script_exists():
    """Test that launch.sh exists and is executable"""
    launch_sh = Path(__file__).parent.parent / 'launch.sh'
    assert launch_sh.exists(), "launch.sh should exist"
    assert launch_sh.stat().st_mode & 0o111, "launch.sh should be executable"


def test_web_interface_exists():
    """Test that web interface HTML exists"""
    web_html = Path(__file__).parent.parent / 'gui' / 'koalas_forge.html'
    assert web_html.exists(), "koalas_forge.html should exist"


def test_server_script_exists():
    """Test that server script exists"""
    server_py = Path(__file__).parent.parent / 'gui' / 'koalas_forge_server.py'
    assert server_py.exists(), "koalas_forge_server.py should exist"
    assert server_py.stat().st_mode & 0o111, "koalas_forge_server.py should be executable"


def test_readme_exists():
    """Test that README exists"""
    readme = Path(__file__).parent.parent / 'README.md'
    assert readme.exists(), "README.md should exist"

    with open(readme, 'r') as f:
        content = f.read()
        assert 'Koala\'s Forge' in content, "README should mention Koala's Forge"


def test_contributing_exists():
    """Test that CONTRIBUTING guide exists"""
    contributing = Path(__file__).parent.parent / 'CONTRIBUTING.md'
    assert contributing.exists(), "CONTRIBUTING.md should exist"


def test_quickstart_exists():
    """Test that QUICKSTART guide exists"""
    quickstart = Path(__file__).parent.parent / 'QUICKSTART.md'
    assert quickstart.exists(), "QUICKSTART.md should exist"


def test_changelog_exists():
    """Test that CHANGELOG exists"""
    changelog = Path(__file__).parent.parent / 'CHANGELOG.md'
    assert changelog.exists(), "CHANGELOG.md should exist"


def test_gitignore_exists():
    """Test that .gitignore exists"""
    gitignore = Path(__file__).parent.parent / '.gitignore'
    assert gitignore.exists(), ".gitignore should exist"


def test_preset_packs_defined():
    """Test that preset packs are defined in HTML"""
    web_html = Path(__file__).parent.parent / 'gui' / 'koalas_forge.html'

    with open(web_html, 'r') as f:
        content = f.read()

    # Check for preset pack definitions
    assert 'ai-developer' in content, "AI Developer preset should be defined"
    assert 'full-stack' in content, "Full Stack preset should be defined"
    assert 'creative' in content, "Creative preset should be defined"
    assert 'gaming' in content, "Gaming preset should be defined"


def test_dry_run_mode_implemented():
    """Test that dry run mode is implemented"""
    web_html = Path(__file__).parent.parent / 'gui' / 'koalas_forge.html'

    with open(web_html, 'r') as f:
        content = f.read()

    assert 'dryRunToggle' in content, "Dry run toggle should exist"
    assert 'Dry Run' in content, "Dry run text should exist"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
