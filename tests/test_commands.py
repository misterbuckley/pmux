"""
Tests for pmux.commands modules.
"""

import pytest
from pmux.core import PMux
from pmux.commands.to import ToCommand
from pmux.commands.env import EnvCommand
from pmux.commands.list import ListCommand
from pmux.commands.custom import CustomCommand


def test_to_command_success(config_file, capsys):
    """Test 'to' command navigates to project."""
    pmux = PMux(config_path=config_file)
    
    class Args:
        project = 'test-project'
        no_autorun = True  # Skip autorun for this test
    
    exit_code = pmux.commands['to'].execute(Args())
    assert exit_code == 0
    
    captured = capsys.readouterr()
    # Should output cd command
    assert "cd /tmp/test-project;" in captured.out
    # Should export env vars from autoload
    assert "export PORT=3000;" in captured.out


def test_to_command_with_alias(config_file, capsys):
    """Test 'to' command works with project alias."""
    pmux = PMux(config_path=config_file)
    
    class Args:
        project = 'tp'  # Alias
        no_autorun = True
    
    exit_code = pmux.commands['to'].execute(Args())
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert "cd /tmp/test-project;" in captured.out


def test_to_command_nonexistent_project(config_file, capsys):
    """Test 'to' command with nonexistent project."""
    pmux = PMux(config_path=config_file)
    
    class Args:
        project = 'nonexistent'
        no_autorun = True
    
    exit_code = pmux.commands['to'].execute(Args())
    assert exit_code == 1
    
    captured = capsys.readouterr()
    assert "no project" in captured.err.lower()


def test_to_command_with_autorun(config_file, capsys):
    """Test 'to' command runs autorun commands."""
    pmux = PMux(config_path=config_file)
    
    class Args:
        project = 'test-project'
        no_autorun = False
    
    exit_code = pmux.commands['to'].execute(Args())
    assert exit_code == 0
    
    captured = capsys.readouterr()
    # Should run autorun commands
    assert "git pull" in captured.out
    assert "npm install" in captured.out


def test_env_command_success(config_file, mock_cwd, capsys):
    """Test 'env' command loads environment."""
    mock_cwd("/tmp/test-project")  # Inside project
    pmux = PMux(config_path=config_file)
    
    class Args:
        environment = 'prod'
    
    exit_code = pmux.commands['env'].execute(Args())
    assert exit_code == 0
    
    captured = capsys.readouterr()
    # Should export prod env vars (including defaults)
    assert "export DEBUG=true;" in captured.out  # from default
    assert "export PORT=80;" in captured.out  # from prod


def test_env_command_not_in_project(config_file, mock_cwd, capsys):
    """Test 'env' command fails when not in a project."""
    mock_cwd("/home/user")  # Outside project
    pmux = PMux(config_path=config_file)
    
    class Args:
        environment = 'local'
    
    exit_code = pmux.commands['env'].execute(Args())
    assert exit_code == 1
    
    captured = capsys.readouterr()
    assert "Not inside a project" in captured.out


def test_env_command_nonexistent_environment(config_file, mock_cwd, capsys):
    """Test 'env' command with nonexistent environment."""
    mock_cwd("/tmp/test-project")
    pmux = PMux(config_path=config_file)
    
    class Args:
        environment = 'nonexistent'
    
    exit_code = pmux.commands['env'].execute(Args())
    assert exit_code == 1
    
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()


def test_list_projects_command(config_file, capsys):
    """Test 'list projects' command."""
    pmux = PMux(config_path=config_file)
    
    class Args:
        list_type = 'projects'
        project_name = None
    
    exit_code = pmux.commands['list'].execute(Args())
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert 'test-project' in captured.out
    assert 'simple-project' in captured.out


def test_list_commands_command(config_file, capsys):
    """Test 'list commands' command."""
    pmux = PMux(config_path=config_file)
    
    class Args:
        list_type = 'commands'
        project_name = None
    
    exit_code = pmux.commands['list'].execute(Args())
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert 'to' in captured.out
    assert 'env' in captured.out
    assert 'global-cmd' in captured.out


def test_list_environments_command(config_file, mock_cwd, capsys):
    """Test 'list environments' command."""
    mock_cwd("/tmp/test-project")
    pmux = PMux(config_path=config_file)
    
    class Args:
        list_type = 'environments'
        project_name = None
    
    exit_code = pmux.commands['list'].execute(Args())
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert 'local' in captured.out
    assert 'prod' in captured.out


def test_custom_command_global(config_file, capsys):
    """Test executing a global custom command."""
    pmux = PMux(config_path=config_file)
    
    assert pmux.custom_command.can_handle('global-cmd')
    
    class Args:
        pass
    
    exit_code = pmux.custom_command.execute(Args())
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert 'Global command' in captured.out


def test_custom_command_project_specific(config_file, mock_cwd, capsys):
    """Test executing a project-specific custom command."""
    mock_cwd("/tmp/test-project")
    pmux = PMux(config_path=config_file)
    
    assert pmux.custom_command.can_handle('start')
    
    class Args:
        pass
    
    exit_code = pmux.custom_command.execute(Args())
    assert exit_code == 0
    
    captured = capsys.readouterr()
    assert 'npm run dev' in captured.out


def test_custom_command_not_found(config_file, capsys):
    """Test custom command not found."""
    pmux = PMux(config_path=config_file)
    
    assert not pmux.custom_command.can_handle('nonexistent')
