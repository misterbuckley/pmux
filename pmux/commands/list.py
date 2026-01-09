"""
'list' command for listing projects, commands, and environments.
"""

import logging

from .base import BaseCommand
from ..output import print_error
from ..utils import get_all_commands, get_environments, find_project


logger = logging.getLogger(__name__)


class ListCommand(BaseCommand):
    """List projects, commands, or environments."""
    
    def execute(self, args):
        """
        Execute the 'list' command.
        
        Args:
            args: Parsed arguments with 'list_type' and optionally 'project_name'
        
        Returns:
            Exit code
        """
        list_type = args.list_type if hasattr(args, 'list_type') else None
        
        if not list_type:
            print_error("Please specify what to list: projects, commands, or environments")
            print_error("Usage:")
            print_error("  pmux list projects")
            print_error("  pmux list commands [project]")
            print_error("  pmux list environments [project]")
            return 1
        
        if list_type == 'projects':
            return self._list_projects()
        elif list_type == 'commands':
            project_name = args.project_name if hasattr(args, 'project_name') else None
            return self._list_commands(project_name)
        elif list_type == 'environments':
            project_name = args.project_name if hasattr(args, 'project_name') else None
            return self._list_environments(project_name)
        else:
            print_error(f"Unknown list type: {list_type}")
            print_error("Available types: projects, commands, environments")
            return 1
    
    def _list_projects(self):
        """List all configured projects."""
        projects = self.config.get('projects', [])
        
        if not projects:
            self.executor.echo("No projects configured.", color="warn")
            return 0
        
        self.executor.echo("Available projects:", color="cyan")
        self.executor.echo("")
        
        for project in sorted(projects, key=lambda p: p.get('name', '')):
            name = project.get('name', 'unnamed')
            root = project.get('root', 'no root')
            
            self.executor.echo(f"  {name}", color="green")
            self.executor.echo(f"    Root: {root}")
            
            if 'aliases' in project and project['aliases']:
                aliases = ', '.join(sorted(project['aliases']))
                self.executor.echo(f"    Aliases: {aliases}")
            
            # Show if it has commands or environments
            if 'commands' in project and project['commands']:
                cmd_count = len(project['commands'])
                self.executor.echo(f"    Commands: {cmd_count} custom command(s)")
            
            if 'env' in project:
                env_names = get_environments(project)
                if env_names:
                    self.executor.echo(f"    Environments: {', '.join(sorted(env_names))}")
            
            self.executor.echo("")
        
        return 0
    
    def _list_commands(self, project_name=None):
        """
        List available commands.
        
        Args:
            project_name: Optional project name to list project-specific commands
        """
        # If project name specified, show commands for that project
        if project_name:
            project = find_project(self.config, project_name)
            if not project:
                print_error(f"Project '{project_name}' not found.")
                return 1
            
            self.executor.echo(f"Commands for project '{project['name']}':", color="cyan")
            self.executor.echo("")
            
            # Built-in commands available everywhere
            self.executor.echo("Built-in commands:", color="yellow")
            for cmd in ['to', 'env', 'config', 'list', 'completion']:
                self.executor.echo(f"  {cmd}", color="green")
            self.executor.echo("")
            
            # Global custom commands
            if 'commands' in self.config and self.config['commands']:
                self.executor.echo("Global commands:", color="yellow")
                for cmd in sorted(self.config['commands'].keys()):
                    self.executor.echo(f"  {cmd}", color="green")
                self.executor.echo("")
            
            # Project-specific commands
            if 'commands' in project and project['commands']:
                self.executor.echo("Project commands:", color="yellow")
                for cmd, bash_cmd in sorted(project['commands'].items()):
                    self.executor.echo(f"  {cmd}", color="green")
                    # Optionally show the command
                    # self.executor.echo(f"    → {bash_cmd}")
                self.executor.echo("")
            else:
                self.executor.echo("No project-specific commands.", color="warn")
        else:
            # Show commands for current context
            self.executor.echo("Available commands:", color="cyan")
            self.executor.echo("")
            
            # Built-in commands
            self.executor.echo("Built-in commands:", color="yellow")
            for cmd in ['to', 'env', 'config', 'list', 'completion']:
                self.executor.echo(f"  {cmd}", color="green")
            self.executor.echo("")
            
            # Global custom commands
            if 'commands' in self.config and self.config['commands']:
                self.executor.echo("Global commands:", color="yellow")
                for cmd in sorted(self.config['commands'].keys()):
                    self.executor.echo(f"  {cmd}", color="green")
                self.executor.echo("")
            
            # Current project commands if in a project
            if self.current_project:
                if 'commands' in self.current_project and self.current_project['commands']:
                    self.executor.echo(f"Commands for current project ({self.current_project['name']}):", color="yellow")
                    for cmd in sorted(self.current_project['commands'].keys()):
                        self.executor.echo(f"  {cmd}", color="green")
                    self.executor.echo("")
        
        return 0
    
    def _list_environments(self, project_name=None):
        """
        List available environments.
        
        Args:
            project_name: Optional project name to list environments for
        """
        # Determine which project to show environments for
        if project_name:
            project = find_project(self.config, project_name)
            if not project:
                print_error(f"Project '{project_name}' not found.")
                return 1
        else:
            project = self.current_project
            if not project:
                print_error("Not in a project. Please specify a project name.")
                print_error("Usage: pmux list environments <project>")
                return 1
        
        # Check if project has environments
        if 'env' not in project:
            self.executor.echo(f"No environments configured for project {project['name']}.", color="warn")
            return 0
        
        env_names = get_environments(project)
        
        if not env_names:
            self.executor.echo(f"No environments configured for project {project['name']}.", color="warn")
            return 0
        
        self.executor.echo(f"Environments for project '{project['name']}':", color="cyan")
        self.executor.echo("")
        
        for env in sorted(env_names):
            self.executor.echo(f"  {env}", color="green")
            
            # Show which is autoload
            if 'autoload' in project['env'] and project['env']['autoload'] == env:
                self.executor.echo("    (autoload)")
        
        self.executor.echo("")
        
        return 0
