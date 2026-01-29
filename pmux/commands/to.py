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
            args: Parsed arguments with 'project', 'autorun', and 'run_command' attributes
        
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
        
        # Run autorun commands if --autorun flag is set
        if hasattr(args, 'autorun') and args.autorun and 'autorun' in project:
            logger.info(f"Running autorun commands")
            for cmd in project['autorun']:
                # In verbose mode, show what we're running
                if self.executor.verbose:
                    self.executor.echo(f"Running: {cmd}", color="info")
                self.executor.run(cmd)
        
        # Run specified command if --run is provided
        if hasattr(args, 'run_command') and args.run_command:
            cmd_name = args.run_command.strip()
            if not cmd_name:
                self.executor.echo("Error: Empty command specified", color="danger")
                return 1
            
            logger.info(f"Running command: {cmd_name}")
            
            # Temporarily set the current project context for command lookup
            # This allows project-specific commands to be found
            original_project = self.core.current_project
            self.core.current_project = project
            
            try:
                # Check if command exists (built-in or custom)
                is_builtin = cmd_name in self.core.commands
                is_custom = self.core.custom_command.can_handle(cmd_name)
                
                if not is_builtin and not is_custom:
                    self.executor.echo(f"Error: Unknown command '{cmd_name}'", color="danger")
                    return 1
                
                # Create a simple args namespace for the command
                import argparse
                cmd_args = argparse.Namespace()
                cmd_args.command = cmd_name
                
                # Execute the command
                exit_code = self.core.run_command(cmd_name, cmd_args)
                if exit_code != 0:
                    return exit_code
            finally:
                # Restore original project context
                self.core.current_project = original_project
        
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
