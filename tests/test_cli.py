"""
Tests for pmux.cli module (end-to-end CLI tests).
"""

import pytest
from pmux.cli import main


def test_cli_custom_command_without_argparse_error(config_file, mock_cwd, capsys):
    """
    Test that custom commands work through the CLI without argparse validation errors.
    
    This is a regression test for the bug where project-specific commands would fail
    with "invalid choice" error from argparse.
    """
    mock_cwd("/tmp/test-project")
    
    # Run the 'start' command (project-specific)
    exit_code = main(['--config', config_file, 'start'])
    
    # Should succeed
    assert exit_code == 0
    
    # Should output the command
    captured = capsys.readouterr()
    assert 'npm run dev' in captured.out
    
    # Should NOT have argparse error
    assert 'invalid choice' not in captured.err
    assert 'error: argument command' not in captured.err


def test_cli_global_custom_command(config_file, capsys):
    """Test that global custom commands work through the CLI."""
    # Run the 'global-cmd' command
    exit_code = main(['--config', config_file, 'global-cmd'])
    
    # Should succeed
    assert exit_code == 0
    
    # Should output the command
    captured = capsys.readouterr()
    assert 'Global command' in captured.out


def test_cli_builtin_command_still_works(config_file, capsys):
    """Test that built-in commands still work after the custom command fix."""
    # Run the 'list projects' command
    exit_code = main(['--config', config_file, 'list', 'projects'])
    
    # Should succeed
    assert exit_code == 0
    
    # Should list projects
    captured = capsys.readouterr()
    assert 'test-project' in captured.out


def test_cli_unknown_command(config_file, capsys):
    """Test that unknown commands are properly rejected."""
    # Run an unknown command
    exit_code = main(['--config', config_file, 'nonexistent-command'])
    
    # Should fail
    assert exit_code == 1
    
    # Should show error
    captured = capsys.readouterr()
    assert 'Command not found' in captured.err
