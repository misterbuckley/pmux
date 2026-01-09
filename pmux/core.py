"""
Core PMux orchestration logic.
"""

import logging

from .executor import BashExecutor
from .config import load_and_validate_config, ConfigError
from .utils import get_current_project
from .output import print_error
from .commands.to import ToCommand
from .commands.env import EnvCommand
from .commands.config_cmd import ConfigCommand
from .commands.list import ListCommand
from .commands.completion import CompletionCommand
from .commands.custom import CustomCommand


logger = logging.getLogger(__name__)


class PMux:
    """
    Main PMux orchestrator.
    
    Manages configuration, current project detection, and command dispatching.
    """
    
    def __init__(self, config_path=None, verbose=False):
        """
        Initialize PMux.
        
        Args:
            config_path: Optional path to config file
            verbose: Whether to show verbose output
        
        Raises:
            ConfigError: If config cannot be loaded or is invalid
        """
        # Load and validate configuration
        self.config, self.config_path = load_and_validate_config(config_path)
        
        # Create executor
        self.executor = BashExecutor(verbose=verbose)
        
        # Detect current project
        self.current_project = get_current_project(self.config)
        
        logger.info(f"Loaded config from: {self.config_path}")
        if self.current_project:
            logger.info(f"Current project: {self.current_project['name']}")
        else:
            logger.debug("Not in a project directory")
        
        # Initialize command handlers
        self._init_commands()
    
    def _init_commands(self):
        """Initialize all command handlers."""
        self.commands = {
            'to': ToCommand(self, self.executor, self.config),
            'env': EnvCommand(self, self.executor, self.config),
            'config': ConfigCommand(self, self.executor, self.config),
            'list': ListCommand(self, self.executor, self.config),
            'completion': CompletionCommand(self, self.executor, self.config),
        }
        
        # Custom command handler
        self.custom_command = CustomCommand(self, self.executor, self.config)
    
    def run_command(self, command_name, args):
        """
        Run a command.
        
        Args:
            command_name: Name of the command to run
            args: Parsed arguments
        
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        logger.debug(f"Running command: {command_name}")
        
        # Check built-in commands first
        if command_name in self.commands:
            return self.commands[command_name].execute(args)
        
        # Check custom commands (global and project-specific)
        if self.custom_command.can_handle(command_name):
            return self.custom_command.execute(args)
        
        # Command not found
        print_error(f"Command not found: {command_name}")
        
        # Let custom command handler suggest similar commands
        self.custom_command.command_name = command_name
        self.custom_command._suggest_similar()
        
        return 1
