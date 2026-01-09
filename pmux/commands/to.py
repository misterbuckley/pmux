"""
'to' command for project navigation.
"""

import logging

from .base import BaseCommand
from ..output import print_error
from ..utils import find_project, expand_path, get_all_project_names, suggest_similar


logger = logging.getLogger(__name__)


class ToCommand(BaseCommand):
    """Navigate to a project directory."""
    
    def execute(self, args):
        """
        Execute the 'to' command.
        
        Args:
            args: Parsed arguments with 'project' and 'no_autorun' attributes
        
        Returns:
            Exit code
        """
        if not args.project:
            print_error("No project provided.")
            self._print_available_projects()
            return 1
        
        # Find the project
        project = find_project(self.config, args.project)
        
        if project is None:
            print_error(f"There is no project '{args.project}' configured.")
            
            # Suggest similar projects
            all_projects = get_all_project_names(self.config)
            suggestions = suggest_similar(args.project, all_projects)
            if suggestions:
                print_error(f"Did you mean: {', '.join(suggestions)}?")
            
            self._print_available_projects()
            return 1
        
        logger.info(f"Navigating to project: {project['name']}")
        
        # Change to project directory
        if 'root' in project:
            project_root = expand_path(project['root'])
            logger.debug(f"cd {project_root}")
            self.executor.cd(project_root)
        else:
            self.executor.echo(f"No root directory configured for project {args.project}", color="danger")
            return 1
        
        # Load autoload environment if configured
        if 'env' in project and 'autoload' in project['env']:
            env_name = project['env']['autoload']
            logger.info(f"Auto-loading environment: {env_name}")
            self._load_environment(project, env_name)
        
        # Run autorun commands unless --no-autorun
        if not args.no_autorun and 'autorun' in project:
            logger.info(f"Running autorun commands")
            for cmd in project['autorun']:
                # In verbose mode, show what we're running
                if self.executor.verbose:
                    self.executor.echo(f"Running: {cmd}", color="info")
                self.executor.run(cmd)
        
        return 0
    
    def _load_environment(self, project, env_name):
        """
        Load environment variables for a project.
        
        Args:
            project: Project dictionary
            env_name: Environment name to load
        """
        env_vars = {}
        
        # Merge default environment if present
        if 'default' in project['env']:
            env_vars = project['env']['default'].copy()
        
        # Merge specified environment
        if env_name in project['env']:
            env_vars.update(project['env'][env_name])
        
        # Export all environment variables
        for variable, value in sorted(env_vars.items()):
            self.executor.export(variable, value)
    
    def _print_available_projects(self):
        """Print available projects to stderr."""
        print_error("\nAvailable projects:")
        for p in sorted(self.config.get('projects', []), key=lambda p: p.get('name', '')):
            name = p.get('name', 'unnamed')
            if 'aliases' in p and p['aliases']:
                aliases = ', '.join(sorted(p['aliases']))
                print_error(f"  {name} (aliases: {aliases})")
            else:
                print_error(f"  {name}")
