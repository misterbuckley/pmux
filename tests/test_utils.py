"""
Tests for pmux.utils module.
"""

import os
import pytest
from pmux.utils import (
    expand_path,
    quote_shell,
    suggest_similar,
    get_current_project,
    find_project,
    get_all_project_names,
    get_all_commands,
    get_environments,
)


def test_expand_path():
    """Test path expansion."""
    # Test tilde expansion
    result = expand_path("~/test")
    assert result.startswith(os.path.expanduser("~"))
    assert result.endswith("test")
    
    # Test absolute path
    result = expand_path("/tmp/test")
    assert result == "/tmp/test"


def test_quote_shell():
    """Test shell quoting."""
    assert quote_shell("simple") == "simple"
    assert quote_shell("with space") == "'with space'"
    assert quote_shell("with'quote") == "'with'\"'\"'quote'"


def test_suggest_similar():
    """Test fuzzy matching suggestions."""
    commands = ["start", "stop", "restart", "status"]
    
    # Close match
    suggestions = suggest_similar("strt", commands)
    assert "start" in suggestions
    
    # No match
    suggestions = suggest_similar("xyz", commands)
    assert len(suggestions) == 0
    
    # Multiple matches
    suggestions = suggest_similar("st", commands, n=3)
    assert len(suggestions) <= 3


def test_get_current_project(sample_config, mock_cwd):
    """Test current project detection."""
    # Inside a project
    mock_cwd("/tmp/test-project")
    project = get_current_project(sample_config)
    assert project is not None
    assert project['name'] == 'test-project'
    
    # Inside a subdirectory of a project
    mock_cwd("/tmp/test-project/src")
    project = get_current_project(sample_config)
    assert project is not None
    assert project['name'] == 'test-project'
    
    # Outside any project
    mock_cwd("/home/user")
    project = get_current_project(sample_config)
    assert project is None


def test_find_project(sample_config):
    """Test project finding by name and alias."""
    # Find by name
    project = find_project(sample_config, 'test-project')
    assert project is not None
    assert project['name'] == 'test-project'
    
    # Find by alias
    project = find_project(sample_config, 'tp')
    assert project is not None
    assert project['name'] == 'test-project'
    
    # Not found
    project = find_project(sample_config, 'nonexistent')
    assert project is None


def test_get_all_project_names(sample_config):
    """Test getting all project names and aliases."""
    names = get_all_project_names(sample_config)
    assert 'test-project' in names
    assert 'tp' in names
    assert 'test' in names
    assert 'simple-project' in names


def test_get_all_commands(sample_config):
    """Test getting all available commands."""
    # Without current project
    commands = get_all_commands(sample_config, None)
    assert 'to' in commands
    assert 'env' in commands
    assert 'global-cmd' in commands
    assert 'start' not in commands  # Project-specific
    
    # With current project
    project = find_project(sample_config, 'test-project')
    commands = get_all_commands(sample_config, project)
    assert 'to' in commands
    assert 'global-cmd' in commands
    assert 'start' in commands  # Project-specific


def test_get_environments(sample_config):
    """Test getting environment names for a project."""
    project = find_project(sample_config, 'test-project')
    envs = get_environments(project)
    
    assert 'local' in envs
    assert 'prod' in envs
    assert 'default' not in envs  # Special keys excluded
    assert 'autoload' not in envs  # Special keys excluded
    
    # Project without environments
    project = find_project(sample_config, 'simple-project')
    envs = get_environments(project)
    assert len(envs) == 0
