"""
Command-line interface for PMux.
"""

import sys
import argparse
import logging

from . import __version__
from .core import PMux
from .config import ConfigError
from .output import print_error


class StderrArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that prints all output to stderr instead of stdout."""
    
    def print_usage(self, file=None):
        if file is None:
            file = sys.stderr
        super().print_usage(file)
    
    def print_help(self, file=None):
        if file is None:
            file = sys.stderr
        super().print_help(file)
    
    def _print_message(self, message, file=None):
        if message:
            if file is None:
                file = sys.stderr
            file.write(message)


def setup_logging(verbosity):
    """
    Setup logging based on verbosity level.
    
    Args:
        verbosity: Number of -v flags (0, 1, or 2+)
    """
    if verbosity == 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG
    
    logging.basicConfig(
        level=level,
        format='[%(levelname)s] %(message)s',
        stream=sys.stderr  # Log to stderr so it doesn't interfere with bash output
    )


def create_parser():
    """
    Create the argument parser.
    
    Returns:
        ArgumentParser instance
    """
    parser = StderrArgumentParser(
        prog='pmux',
        description='Project Multiplexer - Manage multiple projects with ease',
        epilog='Use "pmux <command> --help" for more information about a command.',
        add_help=False  # We'll handle help manually to ensure it goes to stderr
    )
    
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='Show this help message and exit'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version and exit'
    )
    
    parser.add_argument(
        '-v',
        action='count',
        default=0,
        dest='verbosity',
        help='Increase verbosity (-v for INFO, -vv for DEBUG). Also shows commands before running them.'
    )
    
    parser.add_argument(
        '--config',
        metavar='PATH',
        help='Path to configuration file'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # 'to' command
    to_parser = subparsers.add_parser('to', help='Navigate to a project')
    to_parser.add_argument('project', help='Project name or alias')
    to_parser.add_argument(
        '--no-autorun',
        action='store_true',
        help='Skip autorun commands'
    )
    
    # 'env' command
    env_parser = subparsers.add_parser('env', help='Load environment for current project')
    env_parser.add_argument('environment', help='Environment name to load')
    
    # 'config' command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument(
        'config_subcommand',
        nargs='?',
        default='edit',
        choices=['edit', 'validate', 'path'],
        help='Config subcommand (default: edit)'
    )
    
    # 'list' command
    list_parser = subparsers.add_parser('list', help='List projects, commands, or environments')
    list_parser.add_argument(
        'list_type',
        nargs='?',
        choices=['projects', 'commands', 'environments'],
        help='What to list'
    )
    list_parser.add_argument(
        'project_name',
        nargs='?',
        help='Project name (for commands/environments listing)'
    )
    
    # 'completion' command
    completion_parser = subparsers.add_parser('completion', help='Generate shell completion script')
    completion_parser.add_argument(
        'shell',
        nargs='?',
        choices=['bash', 'zsh', 'fish'],
        help='Shell to generate completion for'
    )
    
    return parser


def main(argv=None):
    """
    Main entry point for PMux.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv)
    
    Returns:
        Exit code
    """
    if argv is None:
        argv = sys.argv[1:]
    
    # Create parser and parse known args first
    # This allows us to handle custom commands that aren't defined in argparse
    parser = create_parser()
    
    # If no args, show help
    if not argv:
        parser.print_help(sys.stderr)
        return 1
    
    # Parse known args (this allows unknown custom commands to pass through)
    try:
        args, unknown = parser.parse_known_args(argv)
    except SystemExit as e:
        return e.code if e.code is not None else 1
    
    # Handle help manually
    if hasattr(args, 'help') and args.help:
        parser.print_help(sys.stderr)
        return 0
    
    # Handle version manually
    if hasattr(args, 'version') and args.version:
        print(f'pmux {__version__}', file=sys.stderr)
        return 0
    
    # Setup logging
    setup_logging(args.verbosity)
    
    # Determine if verbose mode should be enabled for executor
    verbose = args.verbosity > 0
    
    # Initialize PMux
    try:
        pmux = PMux(config_path=args.config if hasattr(args, 'config') else None, verbose=verbose)
    except ConfigError as e:
        print_error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        print_error(f"Error initializing PMux: {e}")
        return 1
    
    # If no command specified, check if first arg is a custom command
    if not args.command:
        if argv:
            # Try to handle as custom command
            command_name = argv[0]
            if pmux.custom_command.can_handle(command_name):
                args.command = command_name
            else:
                # Not a known command
                print_error(f"Unknown command: {command_name}")
                print_error("Use 'pmux --help' for a list of commands")
                return 1
        else:
            parser.print_help(sys.stderr)
            return 1
    
    # Run the command
    try:
        exit_code = pmux.run_command(args.command, args)
        return exit_code
    except KeyboardInterrupt:
        print_error("\nInterrupted")
        return 130
    except Exception as e:
        print_error(f"Error running command: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
