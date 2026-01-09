"""
Tests for pmux.config module.
"""

import pytest
import tempfile
from pathlib import Path
from pmux.config import (
    ConfigError,
    ConfigLoader,
    ConfigValidator,
    load_and_validate_config,
)


def test_config_loader_find_config_path(tmp_path, monkeypatch):
    """Test config path finding logic."""
    config_file = tmp_path / "test_config.py"
    config_file.write_text("config = {}")
    
    # Test with explicit argument
    path = ConfigLoader.find_config_path(str(config_file))
    assert path == str(config_file)
    
    # Test with PMUX_CONFIG environment variable
    monkeypatch.setenv('PMUX_CONFIG', str(config_file))
    path = ConfigLoader.find_config_path()
    assert path == str(config_file)
    
    # Test with non-existent file
    with pytest.raises(ConfigError):
        ConfigLoader.find_config_path("/nonexistent/config.py")


def test_config_loader_load_config(tmp_path):
    """Test loading configuration from file."""
    config_file = tmp_path / "config.py"
    config_file.write_text("config = {'test': 'value'}")
    
    config = ConfigLoader.load_config(str(config_file))
    assert config['test'] == 'value'
    
    # Test missing config variable
    bad_file = tmp_path / "bad_config.py"
    bad_file.write_text("other_var = {}")
    
    with pytest.raises(ConfigError, match="must define a 'config' variable"):
        ConfigLoader.load_config(str(bad_file))


def test_config_validator_valid_config():
    """Test validation of valid configuration."""
    valid_config = {
        'projects': [
            {
                'name': 'test',
                'root': '/tmp/test',
                'aliases': ['t'],
                'commands': {'start': 'echo test'},
                'env': {
                    'local': {'VAR': 'value'},
                },
            }
        ],
        'commands': {
            'global': 'echo global',
        },
    }
    
    # Should not raise
    ConfigValidator.validate(valid_config)


def test_config_validator_missing_projects():
    """Test validation fails without projects key."""
    config = {}
    
    with pytest.raises(ConfigError, match="must contain a 'projects' key"):
        ConfigValidator.validate(config)


def test_config_validator_projects_not_list():
    """Test validation fails if projects is not a list."""
    config = {'projects': 'not a list'}
    
    with pytest.raises(ConfigError, match="'projects' must be a list"):
        ConfigValidator.validate(config)


def test_config_validator_project_missing_name():
    """Test validation fails for project without name."""
    config = {
        'projects': [
            {'root': '/tmp/test'}
        ]
    }
    
    with pytest.raises(ConfigError, match="must have a 'name' field"):
        ConfigValidator.validate(config)


def test_config_validator_project_missing_root():
    """Test validation fails for project without root."""
    config = {
        'projects': [
            {'name': 'test'}
        ]
    }
    
    with pytest.raises(ConfigError, match="must have a 'root' field"):
        ConfigValidator.validate(config)


def test_config_validator_invalid_env_autoload():
    """Test validation fails for invalid autoload reference."""
    config = {
        'projects': [
            {
                'name': 'test',
                'root': '/tmp/test',
                'env': {
                    'autoload': 'nonexistent',
                    'local': {'VAR': 'value'},
                },
            }
        ]
    }
    
    with pytest.raises(ConfigError, match="references undefined environment"):
        ConfigValidator.validate(config)


def test_load_and_validate_config(config_file):
    """Test loading and validating config."""
    config, path = load_and_validate_config(config_file)
    
    assert 'projects' in config
    assert len(config['projects']) > 0
    assert path == config_file


def test_load_and_validate_config_not_found(monkeypatch, tmp_path):
    """Test error when config file not found."""
    # Mock the default config path to a non-existent location
    monkeypatch.delenv('PMUX_CONFIG', raising=False)
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setenv('HOME', str(fake_home))
    
    with pytest.raises(ConfigError, match="No configuration file found"):
        load_and_validate_config()
