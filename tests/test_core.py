"""
Tests for pmux.core module.
"""

import pytest
from pmux.core import PMux
from pmux.config import ConfigError


def test_pmux_init(config_file):
    """Test PMux initialization."""
    pmux = PMux(config_path=config_file, verbose=False)
    
    assert pmux.config is not None
    assert pmux.config_path == config_file
    assert pmux.executor is not None
    assert 'to' in pmux.commands
    assert 'env' in pmux.commands
    assert 'config' in pmux.commands
    assert 'list' in pmux.commands
    assert 'completion' in pmux.commands


def test_pmux_init_invalid_config():
    """Test PMux initialization with invalid config."""
    with pytest.raises(ConfigError):
        PMux(config_path="/nonexistent/config.py")


def test_pmux_current_project_detection(config_file, mock_cwd):
    """Test current project detection on init."""
    # Inside a project
    mock_cwd("/tmp/test-project")
    pmux = PMux(config_path=config_file)
    assert pmux.current_project is not None
    assert pmux.current_project['name'] == 'test-project'
    
    # Outside project
    mock_cwd("/home/user")
    pmux = PMux(config_path=config_file)
    assert pmux.current_project is None


def test_pmux_run_builtin_command(config_file):
    """Test running a built-in command."""
    pmux = PMux(config_path=config_file)
    
    # Create mock args
    class Args:
        list_type = 'projects'
        project_name = None
    
    exit_code = pmux.run_command('list', Args())
    assert exit_code == 0


def test_pmux_run_custom_command(config_file, capsys):
    """Test running a custom command."""
    pmux = PMux(config_path=config_file)
    
    class Args:
        pass
    
    # Test global custom command
    exit_code = pmux.run_command('global-cmd', Args())
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert 'Global command' in captured.out


def test_pmux_run_unknown_command(config_file, capsys):
    """Test running an unknown command."""
    pmux = PMux(config_path=config_file)
    
    class Args:
        pass
    
    exit_code = pmux.run_command('unknown-cmd', Args())
    assert exit_code == 1
    
    captured = capsys.readouterr()
    assert 'Command not found' in captured.err
