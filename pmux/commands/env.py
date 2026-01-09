"""
'env' command for environment management.
"""

import logging

from .base import BaseCommand
from ..output import print_error
from ..utils import get_environments


logger = logging.getLogger(__name__)


class EnvCommand(BaseCommand):
    """Load environment variables for the current project."""
    
    def execute(self, args):
        """
        Execute the 'env' command.
        
        Args:
            args: Parsed arguments with 'environment' attribute
        
        Returns:
            Exit code
        """
        # Must be in a project
        if self.current_project is None:
            self.executor.echo("Not inside a project.", color="danger")
            return 1
        
        # Check if project has environments configured
        if 'env' not in self.current_project:
            self.executor.echo(
                f"No environments configured for project {self.current_project['name']}.",
                color="danger"
            )
            return 1
        
        # Check if environment was specified
        if not args.environment:
            self.executor.echo("No environment given.", color="danger")
            self._print_available_environments()
            return 1
        
        env_name = args.environment
        
        # Check if environment exists
        if env_name not in self.current_project['env']:
            self.executor.echo(f"Environment '{env_name}' not found.", color="danger")
            self._print_available_environments()
            return 1
        
        logger.info(f"Loading environment: {env_name} for project {self.current_project['name']}")
        
        # Load the environment
        self._load_environment(env_name)
        
        return 0
    
    def _load_environment(self, env_name):
        """
        Load environment variables from default and specified environment.
        
        Args:
            env_name: Environment name to load
        """
        env_vars = {}
        
        # Merge default environment if present
        if 'default' in self.current_project['env']:
            env_vars = self.current_project['env']['default'].copy()
        
        # Merge specified environment
        if env_name in self.current_project['env']:
            env_vars.update(self.current_project['env'][env_name])
        
        # Export all environment variables
        for variable, value in sorted(env_vars.items()):
            self.executor.export(variable, value)
    
    def _print_available_environments(self):
        """Print available environments for the current project."""
        envs = get_environments(self.current_project)
        
        if envs:
            self.executor.echo("")
            self.executor.echo("Available environments:")
            for env in sorted(envs):
                self.executor.echo(f"  {env}", color="green")
        else:
            self.executor.echo("No environments available.", color="warn")
