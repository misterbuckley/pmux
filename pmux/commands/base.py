"""
Base command class for PMux commands.
"""

from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """
    Abstract base class for all PMux commands.
    """
    
    def __init__(self, core, executor, config):
        """
        Initialize the command.
        
        Args:
            core: PMux core instance
            executor: BashExecutor instance
            config: Configuration dictionary
        """
        self.core = core
        self.executor = executor
        self.config = config
    
    @abstractmethod
    def execute(self, args):
        """
        Execute the command.
        
        Args:
            args: Command arguments (list)
        
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        pass
    
    @property
    def current_project(self):
        """Get the current project from core."""
        return self.core.current_project
