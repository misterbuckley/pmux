"""
Custom command handler for global and project-specific commands.
"""

import logging

from .base import BaseCommand
from ..output import print_error
from ..utils import get_all_commands, suggest_similar


logger = logging.getLogger(__name__)


class CustomCommand(BaseCommand):
    """Handle custom commands (global and project-specific)."""
    
    def __init__(self, core, executor, config):
        """
        Initialize the custom command handler.
        
        Args:
            core: PMux core instance
            executor: BashExecutor instance
            config: Configuration dictionary
        """
        super().__init__(core, executor, config)
        self.command_name = None
    
    def can_handle(self, command_name):
        """
        Check if this handler can handle the given command.
        
        Args:
            command_name: Name of the command to check
        
        Returns:
            True if command exists, False otherwise
        """
        self.command_name = command_name
        
        # Check global commands
        if 'commands' in self.config and command_name in self.config['commands']:
            return True
        
        # Check project-specific commands
        if self.current_project and 'commands' in self.current_project:
            if command_name in self.current_project['commands']:
                return True
        
        return False
    
    def execute(self, args):
        """
        Execute the custom command.
        
        Args:
            args: Parsed arguments
        
        Returns:
            Exit code
        """
        if not self.command_name:
            print_error("No command specified")
            return 1
        
        # Get the bash command to run
        bash_command = self._get_bash_command()
        
        if bash_command is None:
            print_error(f"Command not found: {self.command_name}")
            self._suggest_similar()
            return 1
        
        logger.info(f"Running custom command: {self.command_name}")
        
        # Run the command (executor handles verbose display)
        self.executor.run(bash_command)
        
        return 0
    
    def _get_bash_command(self):
        """
        Get the bash command string for the custom command.
        
        Returns:
            Bash command string or None if not found
        """
        # Check project-specific commands first (more specific)
        if self.current_project and 'commands' in self.current_project:
            if self.command_name in self.current_project['commands']:
                return self.current_project['commands'][self.command_name]
        
        # Check global commands
        if 'commands' in self.config and self.command_name in self.config['commands']:
            return self.config['commands'][self.command_name]
        
        return None
    
    def _suggest_similar(self):
        """Suggest similar commands if the command wasn't found."""
        all_commands = get_all_commands(self.config, self.current_project)
        suggestions = suggest_similar(self.command_name, all_commands)
        
        if suggestions:
            print_error(f"Did you mean: {', '.join(suggestions)}?")
