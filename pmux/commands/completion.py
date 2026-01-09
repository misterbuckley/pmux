"""
'completion' command for shell completion script generation.
"""

import os
import logging

from .base import BaseCommand
from ..output import print_error, print_info


logger = logging.getLogger(__name__)


class CompletionCommand(BaseCommand):
    """Generate shell completion scripts."""
    
    def execute(self, args):
        """
        Execute the 'completion' command.
        
        Args:
            args: Parsed arguments with 'shell' attribute
        
        Returns:
            Exit code
        """
        shell = args.shell if hasattr(args, 'shell') else None
        
        if not shell:
            print_error("Please specify a shell: bash, zsh, or fish")
            print_error("Usage: pmux completion <shell>")
            return 1
        
        if shell not in ['bash', 'zsh', 'fish']:
            print_error(f"Unsupported shell: {shell}")
            print_error("Supported shells: bash, zsh, fish")
            return 1
        
        # Get the completion script
        script = self._get_completion_script(shell)
        
        if script:
            # Output the script directly to stdout (not through executor)
            print_info(script)
            print_info("")
            print_info(f"# To enable completion, add this to your ~/.{shell}rc:")
            print_info(f"#   eval \"$(pmux completion {shell})\"")
            return 0
        else:
            print_error(f"Completion script for {shell} not found")
            return 1
    
    def _get_completion_script(self, shell):
        """
        Get the completion script for the specified shell.
        
        Args:
            shell: Shell name (bash, zsh, fish)
        
        Returns:
            Completion script as string
        """
        if shell == 'bash':
            return self._bash_completion()
        elif shell == 'zsh':
            return self._zsh_completion()
        elif shell == 'fish':
            return self._fish_completion()
        return None
    
    def _bash_completion(self):
        """Generate bash completion script."""
        return """# Bash completion for pmux
_pmux_completion() {
    local cur prev commands projects
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Main commands
    commands="to env config list completion"
    
    # Get projects from pmux
    projects=$(pmux list projects 2>/dev/null | grep -E "^  [a-zA-Z]" | awk '{print $1}')
    
    case "${prev}" in
        pmux)
            # Complete main commands and projects
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            return 0
            ;;
        to)
            # Complete project names
            COMPREPLY=( $(compgen -W "${projects}" -- ${cur}) )
            return 0
            ;;
        env)
            # Complete environment names (would need current project context)
            return 0
            ;;
        config)
            # Complete config subcommands
            COMPREPLY=( $(compgen -W "edit validate path" -- ${cur}) )
            return 0
            ;;
        list)
            # Complete list types
            COMPREPLY=( $(compgen -W "projects commands environments" -- ${cur}) )
            return 0
            ;;
        completion)
            # Complete shell names
            COMPREPLY=( $(compgen -W "bash zsh fish" -- ${cur}) )
            return 0
            ;;
    esac
}

complete -F _pmux_completion pmux"""
    
    def _zsh_completion(self):
        """Generate zsh completion script."""
        return """# Zsh completion for pmux
#compdef pmux

_pmux() {
    local line state
    
    _arguments -C \
        "1: :->cmds" \
        "*::arg:->args"
    
    case "$state" in
        cmds)
            _values 'pmux commands' \
                'to[Navigate to project]' \
                'env[Load environment]' \
                'config[Manage configuration]' \
                'list[List projects/commands/environments]' \
                'completion[Generate shell completion]'
            ;;
        args)
            case "$line[1]" in
                to)
                    # Complete project names
                    local projects
                    projects=(${(f)"$(pmux list projects 2>/dev/null | grep -E '^  [a-zA-Z]' | awk '{print $1}')"})
                    _values 'projects' $projects
                    ;;
                config)
                    _values 'config subcommands' \
                        'edit[Edit configuration file]' \
                        'validate[Validate configuration]' \
                        'path[Show config file path]'
                    ;;
                list)
                    _values 'list types' \
                        'projects[List all projects]' \
                        'commands[List available commands]' \
                        'environments[List environments]'
                    ;;
                completion)
                    _values 'shells' 'bash' 'zsh' 'fish'
                    ;;
            esac
            ;;
    esac
}

_pmux"""
    
    def _fish_completion(self):
        """Generate fish completion script."""
        return r"""# Fish completion for pmux

# Main commands
complete -c pmux -f -n "__fish_use_subcommand" -a "to" -d "Navigate to project"
complete -c pmux -f -n "__fish_use_subcommand" -a "env" -d "Load environment"
complete -c pmux -f -n "__fish_use_subcommand" -a "config" -d "Manage configuration"
complete -c pmux -f -n "__fish_use_subcommand" -a "list" -d "List projects/commands/environments"
complete -c pmux -f -n "__fish_use_subcommand" -a "completion" -d "Generate shell completion"

# to command - complete with project names
complete -c pmux -f -n "__fish_seen_subcommand_from to" -a "(pmux list projects 2>/dev/null | grep -E '^  [a-zA-Z]' | awk '{print \$1}')"

# config subcommands
complete -c pmux -f -n "__fish_seen_subcommand_from config" -a "edit" -d "Edit configuration file"
complete -c pmux -f -n "__fish_seen_subcommand_from config" -a "validate" -d "Validate configuration"
complete -c pmux -f -n "__fish_seen_subcommand_from config" -a "path" -d "Show config file path"

# list subcommands
complete -c pmux -f -n "__fish_seen_subcommand_from list" -a "projects" -d "List all projects"
complete -c pmux -f -n "__fish_seen_subcommand_from list" -a "commands" -d "List available commands"
complete -c pmux -f -n "__fish_seen_subcommand_from list" -a "environments" -d "List environments"

# completion shells
complete -c pmux -f -n "__fish_seen_subcommand_from completion" -a "bash" -d "Bash completion"
complete -c pmux -f -n "__fish_seen_subcommand_from completion" -a "zsh" -d "Zsh completion"
complete -c pmux -f -n "__fish_seen_subcommand_from completion" -a "fish" -d "Fish completion"
"""
