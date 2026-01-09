"""
Pytest fixtures and configuration for PMux tests.
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'commands': {
            'global-cmd': 'echo "Global command"',
        },
        'projects': [
            {
                'name': 'test-project',
                'root': '/tmp/test-project',
                'aliases': ['tp', 'test'],
                'commands': {
                    'start': 'npm run dev',
                    'test': 'pytest',
                },
                'env': {
                    'autoload': 'local',
                    'default': {
                        'DEBUG': 'true',
                    },
                    'local': {
                        'PORT': '3000',
                        'HOST': 'localhost',
                    },
                    'prod': {
                        'PORT': '80',
                        'HOST': '0.0.0.0',
                    },
                },
                'autorun': [
                    'git pull',
                    'npm install',
                ],
            },
            {
                'name': 'simple-project',
                'root': '/tmp/simple-project',
            },
        ],
    }


@pytest.fixture
def config_file(tmp_path, sample_config):
    """Create a temporary config file."""
    config_path = tmp_path / "config.py"
    config_path.write_text(f"config = {sample_config!r}")
    return str(config_path)


@pytest.fixture
def mock_cwd(monkeypatch, tmp_path):
    """Mock current working directory."""
    def set_cwd(path):
        monkeypatch.setattr(os, 'getcwd', lambda: str(path))
    return set_cwd
