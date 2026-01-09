from setuptools import setup, find_packages

setup(
    name="pmux",
    version="1.0.0",
    description="Project Multiplexer - Manage multiple projects with ease",
    author="Michael Buckley",
    packages=find_packages(),
    install_requires=[
        # No external dependencies - uses only Python stdlib
    ],
    entry_points={
        'console_scripts': [
            'pmux=pmux.cli:main',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
