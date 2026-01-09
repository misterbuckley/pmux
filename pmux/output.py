"""
Output formatting and color utilities for PMux.
"""

import sys


# ANSI color codes
COLORS = {
    "none": r"\033[1;0m",
    "black": r"\033[1;30m",
    "red": r"\033[1;31m",
    "danger": r"\033[1;31m",
    "green": r"\033[1;32m",
    "success": r"\033[1;32m",
    "yellow": r"\033[1;33m",
    "warn": r"\033[1;33m",
    "blue": r"\033[1;34m",
    "purple": r"\033[1;35m",
    "cyan": r"\033[1;36m",
    "info": r"\033[1;36m",
    "white": r"\033[1;37m",
}


def print_error(message):
    """Print an error message to stderr."""
    print(message, file=sys.stderr)


def print_info(message):
    """Print an info message to stdout."""
    print(message, file=sys.stdout)


def colorize(text, color=None):
    """
    Return text with color codes wrapped around it.
    
    Args:
        text: The text to colorize
        color: Color name from COLORS dict (optional)
    
    Returns:
        Colored text string
    """
    if color and color in COLORS:
        return f"{COLORS[color]}{text}{COLORS['none']}"
    return text
