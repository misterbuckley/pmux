# PMux - Project Multiplexer

A powerful command-line tool for managing multiple projects with environment configurations and custom commands.

## Features

- **Project Navigation**: Quickly switch between projects with cd and automatic setup
- **Environment Management**: Load different environment variables for local, dev, prod, etc.
- **Custom Commands**: Define global and project-specific commands
- **Autorun Scripts**: Automatically run commands when entering a project
- **Shell Completion**: Tab completion for bash, zsh, and fish
- **Configuration Validation**: Validate your configuration file with helpful error messages
- **Verbose Mode**: See exactly what commands are being run with all environment variables expanded

## Installation

```bash
# Clone or download the repository
cd /path/to/pmux

# Install pmux
pip install -e .

# Or run directly with the script
chmod +x pmux_script
```

## Configuration

PMux looks for configuration in the following locations (in order):

1. Path specified with `--config` flag
2. `$PMUX_CONFIG` environment variable
3. `~/.config/pmux/config.py`

### Configuration File Format

The configuration file is a Python file that defines a `config` dictionary:

```python
config = {
    # Global commands available everywhere
    'commands': {
        'use-local-buffet': 'rm -rf ./node_modules/@company/lib && cp -r ~/Projects/lib ./node_modules/@company/',
    },
    
    # List of projects
    'projects': [
        {
            'name': 'my-project',
            'root': '~/Projects/my-project',
            'aliases': ['mp', 'myp'],  # Optional aliases
            
            # Optional: Project-specific commands
            'commands': {
                'start': 'npm run dev',
                'test': 'pytest tests/',
            },
            
            # Optional: Environment variables
            'env': {
                'autoload': 'local',  # Auto-load this environment when entering project
                'default': {
                    'DEBUG': 'true',
                },
                'local': {
                    'PORT': '3000',
                    'HOST': 'localhost',
                },
                'prod': {
                    'PORT': '80',
                    'HOST': '0.0.0.0',
                },
            },
            
            # Optional: Commands to run when entering project
            'autorun': [
                'git pull',
                'npm install',
            ],
        },
    ],
}
```

## Usage

### Basic Commands

```bash
# Navigate to a project (by name or alias)
pmux to my-project
# or with alias
pmux to mp

# Navigate without running autorun commands
pmux to my-project --no-autorun

# Load an environment
pmux env prod

# List all projects
pmux list projects

# List all available commands
pmux list commands

# List commands for a specific project
pmux list commands my-project

# List environments for current project
pmux list environments

# Manage configuration
pmux config edit      # Edit config file
pmux config validate  # Validate config
pmux config path      # Show config file path

# Generate shell completion
pmux completion bash
pmux completion zsh
pmux completion fish

# Run custom commands
pmux start  # Runs project-specific 'start' command
pmux use-local-buffet  # Runs global 'use-local-buffet' command
```

### Verbose Mode

Use `-v` to see commands before they're run with all environment variables expanded:

```bash
# Single -v shows INFO level logs and command expansion
pmux -v to my-project

# Double -vv shows DEBUG level logs
pmux -vv to my-project
```

Example output with `-v`:
```
Running: PORT=3000 HOST=localhost DEBUG=true npm run dev
```

### Shell Integration

PMux outputs bash commands that need to be sourced by your shell. Create a function (not an alias) in your shell rc file:

```bash
# ~/.bashrc or ~/.zshrc
pmux() {
    eval "$(/path/to/pmux/pmux_script "$@")"
}

# Or if installed via pip
pmux() {
    eval "$(command pmux "$@")"
}
```

**Important**: Use a shell function, not an alias, to ensure arguments are passed correctly.

### Shell Completion

Enable tab completion for your shell:

```bash
# Bash
eval "$(pmux completion bash)"

# Zsh
eval "$(pmux completion zsh)"

# Fish
pmux completion fish | source
```

Add the appropriate line to your shell's rc file to enable permanently.

## Examples

### Navigate to a project with autoload environment

```bash
$ pmux to my-project
# Changes directory to ~/Projects/my-project
# Loads 'local' environment (autoload)
# Runs: git pull
# Runs: npm install
```

### Load a different environment

```bash
$ pmux env prod
# Exports: DEBUG=true (from default)
# Exports: PORT=80 (from prod)
# Exports: HOST=0.0.0.0 (from prod)
```

### Run a project-specific command

```bash
$ pmux start
# Runs: npm run dev (with all environment variables)
```

### Verbose output

```bash
$ pmux -v start
# Shows: Running: PORT=3000 HOST=localhost DEBUG=true npm run dev
# Runs: npm run dev
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=pmux --cov-report=html
```

All 43 tests should pass, covering:
- Configuration loading and validation
- Project detection
- Command execution
- Environment management
- Shell output generation
- Utility functions

## Architecture

PMux is designed with modularity in mind:

```
pmux/
├── __init__.py           # Package metadata
├── cli.py                # Argument parsing and entry point
├── core.py               # Main orchestration logic
├── config.py             # Configuration loading and validation
├── executor.py           # Bash command output handler
├── output.py             # Output formatting and colors
├── utils.py              # Utility functions
└── commands/             # Command handlers
    ├── base.py           # Abstract base class
    ├── to.py             # Project navigation
    ├── env.py            # Environment management
    ├── config_cmd.py     # Config management
    ├── list.py           # List projects/commands/environments
    ├── custom.py         # Custom command handler
    └── completion.py     # Shell completion generation
```

## Requirements

- Python 3.6+
- No external dependencies (uses only Python stdlib)

## License

This project is available under your chosen license.

## Author

Michael Buckley
