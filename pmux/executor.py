"""
Bash command executor for PMux.
Outputs bash commands to stdout for sourcing/eval.
"""

import sys
import logging

from .output import COLORS, colorize
from .utils import quote_shell


logger = logging.getLogger(__name__)


class BashExecutor:
    """
    Outputs bash commands to stdout for sourcing by the parent shell.
    
    In verbose mode, tracks environment variables and displays the full
    command with all env vars expanded before running it.
    """
    
    def __init__(self, verbose=False):
        """
        Initialize the executor.
        
        Args:
            verbose: Whether to show commands before running them
        """
        self.verbose = verbose
        self.env_vars = []  # Track env vars for verbose display
    
    def _write(self, command, predicate=None):
        """
        Write a bash command to stdout.
        
        Args:
            command: The command to write
            predicate: Optional arguments/predicate for the command
        """
        if predicate:
            sys.stdout.write(f"{command} {predicate};\n")
        else:
            sys.stdout.write(f"{command};\n")
    
    def cd(self, directory):
        """
        Output a cd command.
        
        Args:
            directory: Directory to change to
        """
        logger.debug(f"cd {directory}")
        self._write("cd", quote_shell(directory))
    
    def export(self, variable, value):
        """
        Output an export command and track the env var for verbose display.
        
        Args:
            variable: Environment variable name
            value: Value to set
        """
        logger.debug(f"export {variable}={value}")
        
        # Track env var for verbose display
        self.env_vars.append((variable, value))
        
        self._write("export", f"{variable}={quote_shell(str(value))}")
    
    def run(self, command):
        """
        Output an arbitrary bash command.
        
        If verbose mode is enabled and env vars have been tracked,
        displays the command with all env vars before running it.
        
        Args:
            command: Bash command to run
        """
        logger.debug(f"run: {command}")
        
        # Show command with env vars in verbose mode
        if self.verbose and self.env_vars:
            self._show_command(command)
        
        self._write(command)
    
    def echo(self, message, color=None):
        """
        Output an echo command.
        
        Args:
            message: Message to echo
            color: Optional color name
        """
        if color:
            colored_msg = colorize(str(message), color)
            self._write("echo -e", quote_shell(colored_msg))
        else:
            self._write("echo", quote_shell(str(message)))
    
    def _show_command(self, command):
        """
        Display the command that will be executed with environment variables.
        
        Args:
            command: The command to display
        """
        env_prefix = " ".join([f"{var}={quote_shell(str(val))}" for var, val in self.env_vars])
        
        if env_prefix:
            display_cmd = f"{env_prefix} {command}"
        else:
            display_cmd = command
        
        self.echo(f"Running: {display_cmd}", color="info")
        
        # Clear env vars for next command
        self.env_vars = []
    
    def clear_env_vars(self):
        """Clear tracked environment variables."""
        self.env_vars = []
