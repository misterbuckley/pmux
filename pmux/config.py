"""
Configuration loading and validation for PMux.
"""

import os
import sys
import importlib.util
from pathlib import Path

from .output import print_error
from .utils import expand_path


class ConfigError(Exception):
    """Raised when there's an error with the configuration."""
    pass


class ConfigLoader:
    """Loads PMux configuration from various locations."""
    
    @staticmethod
    def find_config_path(config_arg=None):
        """
        Find the configuration file path.
        
        Priority order:
        1. --config argument
        2. PMUX_CONFIG environment variable
        3. ~/.config/pmux/config.py
        
        Args:
            config_arg: Path from --config argument (optional)
        
        Returns:
            Path to config file, or None if not found
        """
        # 1. Check --config argument
        if config_arg:
            path = expand_path(config_arg)
            if os.path.isfile(path):
                return path
            else:
                raise ConfigError(f"Config file not found: {path}")
        
        # 2. Check PMUX_CONFIG environment variable
        if 'PMUX_CONFIG' in os.environ:
            path = expand_path(os.environ['PMUX_CONFIG'])
            if os.path.isfile(path):
                return path
            else:
                raise ConfigError(f"Config file from PMUX_CONFIG not found: {path}")
        
        # 3. Check ~/.config/pmux/config.py
        default_path = expand_path("~/.config/pmux/config.py")
        if os.path.isfile(default_path):
            return default_path
        
        return None
    
    @staticmethod
    def load_config(config_path):
        """
        Load configuration from a Python file.
        
        Args:
            config_path: Path to the config file
        
        Returns:
            Configuration dictionary
        
        Raises:
            ConfigError: If config cannot be loaded
        """
        try:
            # Load the Python module dynamically
            spec = importlib.util.spec_from_file_location("pmux_config", config_path)
            if spec is None or spec.loader is None:
                raise ConfigError(f"Cannot load config file: {config_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the 'config' variable from the module
            if not hasattr(module, 'config'):
                raise ConfigError(f"Config file must define a 'config' variable: {config_path}")
            
            return module.config
        
        except Exception as e:
            if isinstance(e, ConfigError):
                raise
            raise ConfigError(f"Error loading config file: {e}")


class ConfigValidator:
    """Validates PMux configuration structure."""
    
    @staticmethod
    def validate(config, config_path=None):
        """
        Validate the configuration structure.
        
        Args:
            config: Configuration dictionary to validate
            config_path: Path to config file (for error messages)
        
        Raises:
            ConfigError: If validation fails
        """
        errors = []
        
        # Check that config is a dictionary
        if not isinstance(config, dict):
            raise ConfigError("Config must be a dictionary")
        
        # Check for required 'projects' key
        if 'projects' not in config:
            errors.append("Config must contain a 'projects' key")
        elif not isinstance(config['projects'], list):
            errors.append("'projects' must be a list")
        else:
            # Validate each project
            for i, project in enumerate(config['projects']):
                ConfigValidator._validate_project(project, i, errors)
        
        # Validate global commands if present
        if 'commands' in config:
            if not isinstance(config['commands'], dict):
                errors.append("'commands' must be a dictionary")
        
        # Raise error if any validation failed
        if errors:
            error_msg = "Configuration validation failed"
            if config_path:
                error_msg += f" ({config_path})"
            error_msg += ":\n  - " + "\n  - ".join(errors)
            raise ConfigError(error_msg)
    
    @staticmethod
    def _validate_project(project, index, errors):
        """
        Validate a single project configuration.
        
        Args:
            project: Project dictionary
            index: Project index in the list
            errors: List to append errors to
        """
        prefix = f"Project {index}"
        
        # Must be a dictionary
        if not isinstance(project, dict):
            errors.append(f"{prefix} must be a dictionary")
            return
        
        # Must have 'name'
        if 'name' not in project:
            errors.append(f"{prefix} must have a 'name' field")
        elif not isinstance(project['name'], str):
            errors.append(f"{prefix} 'name' must be a string")
        else:
            prefix = f"Project '{project['name']}'"
        
        # Must have 'root'
        if 'root' not in project:
            errors.append(f"{prefix} must have a 'root' field")
        elif not isinstance(project['root'], str):
            errors.append(f"{prefix} 'root' must be a string")
        
        # Validate optional fields
        if 'aliases' in project and not isinstance(project['aliases'], list):
            errors.append(f"{prefix} 'aliases' must be a list")
        
        if 'commands' in project and not isinstance(project['commands'], dict):
            errors.append(f"{prefix} 'commands' must be a dictionary")
        
        if 'autorun' in project and not isinstance(project['autorun'], list):
            errors.append(f"{prefix} 'autorun' must be a list")
        
        if 'env' in project:
            ConfigValidator._validate_env(project['env'], prefix, errors)
    
    @staticmethod
    def _validate_env(env, prefix, errors):
        """
        Validate environment configuration.
        
        Args:
            env: Environment dictionary
            prefix: Prefix for error messages
            errors: List to append errors to
        """
        if not isinstance(env, dict):
            errors.append(f"{prefix} 'env' must be a dictionary")
            return
        
        # Check autoload if present
        if 'autoload' in env:
            if not isinstance(env['autoload'], str):
                errors.append(f"{prefix} 'env.autoload' must be a string")
            elif env['autoload'] not in env:
                errors.append(f"{prefix} 'env.autoload' references undefined environment '{env['autoload']}'")
        
        # Each environment should be a dictionary of env vars
        for env_name, env_vars in env.items():
            if env_name in ('autoload',):
                continue
            if not isinstance(env_vars, dict):
                errors.append(f"{prefix} 'env.{env_name}' must be a dictionary")


def load_and_validate_config(config_arg=None):
    """
    Load and validate configuration.
    
    Args:
        config_arg: Path from --config argument (optional)
    
    Returns:
        Tuple of (config_dict, config_path)
    
    Raises:
        ConfigError: If config cannot be loaded or is invalid
    """
    # Find config file
    config_path = ConfigLoader.find_config_path(config_arg)
    if config_path is None:
        raise ConfigError(
            "No configuration file found. Please create one at:\n"
            "  ~/.config/pmux/config.py\n"
            "Or set PMUX_CONFIG environment variable, or use --config flag."
        )
    
    # Load config
    config = ConfigLoader.load_config(config_path)
    
    # Validate config
    ConfigValidator.validate(config, config_path)
    
    return config, config_path
