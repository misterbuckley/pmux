"""
Tests for pmux.executor module.
"""

import sys
from io import StringIO
import pytest
from pmux.executor import BashExecutor


def test_executor_cd(capsys):
    """Test cd command output."""
    executor = BashExecutor()
    executor.cd("/tmp/test")
    
    captured = capsys.readouterr()
    assert "cd /tmp/test;" in captured.out


def test_executor_export(capsys):
    """Test export command output."""
    executor = BashExecutor()
    executor.export("TEST_VAR", "test_value")
    
    captured = capsys.readouterr()
    assert "export TEST_VAR=test_value;" in captured.out


def test_executor_run(capsys):
    """Test running arbitrary command."""
    executor = BashExecutor()
    executor.run("echo 'hello world'")
    
    captured = capsys.readouterr()
    assert "echo 'hello world';" in captured.out


def test_executor_echo(capsys):
    """Test echo command with color."""
    executor = BashExecutor()
    executor.echo("Test message", color="green")
    
    captured = capsys.readouterr()
    assert "echo" in captured.out
    assert "Test message" in captured.out
    assert r"\033[1;32m" in captured.out  # Green color code


def test_executor_verbose_mode(capsys):
    """Test verbose mode shows commands with env vars."""
    executor = BashExecutor(verbose=True)
    
    # Track env vars
    executor.export("FOO", "bar")
    executor.export("BAZ", "qux")
    
    # Run command (should show env vars)
    executor.run("npm run dev")
    
    captured = capsys.readouterr()
    output = captured.out
    
    # Should contain the command
    assert "npm run dev" in output
    # Should show Running: message
    assert "Running:" in output


def test_executor_clear_env_vars():
    """Test clearing tracked env vars."""
    executor = BashExecutor(verbose=True)
    
    executor.export("TEST", "value")
    assert len(executor.env_vars) > 0
    
    executor.clear_env_vars()
    assert len(executor.env_vars) == 0
