"""
Utility functions for PMux.
"""

import os
import shlex
import difflib
from pathlib import Path


def expand_path(path):
    """
    Expand ~ and environment variables in a path.
    
    Args:
        path: Path string to expand
    
    Returns:
        Expanded absolute path
    """
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


def quote_shell(value):
    """
    Properly quote a value for safe use in shell commands.
    
    Args:
        value: Value to quote
    
    Returns:
        Shell-quoted string
    """
    return shlex.quote(str(value))


def suggest_similar(invalid, valid_list, cutoff=0.6, n=3):
    """
    Suggest similar strings from a list using fuzzy matching.
    
    Args:
        invalid: The invalid string to match against
        valid_list: List of valid strings to search
        cutoff: Similarity threshold (0.0 to 1.0)
        n: Maximum number of suggestions
    
    Returns:
        List of suggested strings
    """
    return difflib.get_close_matches(invalid, valid_list, n=n, cutoff=cutoff)


def get_current_project(config):
    """
    Determine the current project based on the current working directory.
    
    Uses os.path.commonpath to check if cwd is within a project's root directory.
    This is more robust than simple string prefix matching.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Project dictionary if found, None otherwise
    """
    cwd = os.getcwd()
    
    for project in config.get('projects', []):
        if 'root' not in project:
            continue
        
        project_root = expand_path(project['root'])
        
        try:
            # Check if cwd is within project_root
            # os.path.commonpath returns the common path prefix
            common = os.path.commonpath([cwd, project_root])
            # If the common path is the project root, we're inside the project
            if common == project_root:
                return project
        except ValueError:
            # Different drives on Windows, or one path is relative
            continue
    
    return None


def find_project(config, name):
    """
    Find a project by name or alias.
    
    Args:
        config: Configuration dictionary
        name: Project name or alias to search for
    
    Returns:
        Project dictionary if found, None otherwise
    """
    for project in config.get('projects', []):
        # Check project name
        if project.get('name') == name:
            return project
        
        # Check aliases
        if 'aliases' in project and name in project['aliases']:
            return project
    
    return None


def get_all_project_names(config):
    """
    Get all project names and aliases.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        List of project names and aliases
    """
    names = []
    for project in config.get('projects', []):
        if 'name' in project:
            names.append(project['name'])
        if 'aliases' in project:
            names.extend(project['aliases'])
    return names


def get_all_commands(config, current_project=None):
    """
    Get all available commands (global and project-specific if applicable).
    
    Args:
        config: Configuration dictionary
        current_project: Current project dictionary (optional)
    
    Returns:
        List of command names
    """
    commands = ['to', 'env', 'config', 'list', 'completion']
    
    # Add global custom commands
    if 'commands' in config:
        commands.extend(config['commands'].keys())
    
    # Add project-specific commands if in a project
    if current_project and 'commands' in current_project:
        commands.extend(current_project['commands'].keys())
    
    return commands


def get_environments(project):
    """
    Get all environment names for a project.
    
    Args:
        project: Project dictionary
    
    Returns:
        List of environment names (excluding 'default' and 'autoload')
    """
    if 'env' not in project:
        return []
    
    # Filter out special keys like 'default' and 'autoload'
    return [key for key in project['env'].keys() 
            if key not in ('default', 'autoload')]
