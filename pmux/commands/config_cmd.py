"""
'config' command for configuration management.
"""

import os
import logging
import subprocess

from .base import BaseCommand
from ..output import print_error, print_info
from ..config import ConfigValidator, ConfigError


logger = logging.getLogger(__name__)


class ConfigCommand(BaseCommand):
    """Manage PMux configuration."""
    
    def __init__(self, core, executor, config):
        """
        Initialize the config command.
        
        Args:
            core: PMux core instance
            executor: BashExecutor instance
            config: Configuration dictionary
        """
        super().__init__(core, executor, config)
        self.config_path = core.config_path
    
    def execute(self, args):
        """
        Execute the 'config' command.
        
        Args:
            args: Parsed arguments with 'config_subcommand' attribute
        
        Returns:
            Exit code
        """
        subcommand = args.config_subcommand if hasattr(args, 'config_subcommand') else 'edit'
        
        if subcommand == 'edit':
            return self._edit_config()
        elif subcommand == 'validate':
            return self._validate_config()
        elif subcommand == 'path':
            return self._show_path()
        else:
            print_error(f"Unknown config subcommand: {subcommand}")
            print_error("Available subcommands: edit, validate, path")
            return 1
    
    def _edit_config(self):
        """
        Open the config file in the user's editor.
        
        Returns:
            Exit code
        """
        # Get editor from environment or default to vim
        editor = os.environ.get('EDITOR', 'vim')
        
        # Since we output bash commands, we need to output the editor command
        # Use </dev/tty to ensure editor can read from terminal
        self.executor.run(f"{editor} {self.config_path} </dev/tty")
        
        return 0
    
    def _validate_config(self):
        """
        Validate the configuration file.
        
        Returns:
            Exit code
        """
        try:
            ConfigValidator.validate(self.config, self.config_path)
            print_info(f"✓ Configuration is valid: {self.config_path}")
            return 0
        except ConfigError as e:
            print_error(f"✗ Configuration validation failed:")
            print_error(str(e))
            return 1
    
    def _show_path(self):
        """
        Show the path to the active config file.
        
        Returns:
            Exit code
        """
        print_info(self.config_path)
        return 0
