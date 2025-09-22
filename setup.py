#!/usr/bin/env python3
"""Setup script for Dolibarr MCP package."""

from setuptools import setup, find_packages
import os

# Read the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dolibarr-mcp',
    version='1.0.0',
    description='Professional Model Context Protocol server for complete Dolibarr ERP management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/latinogino/dolibarr-mcp',
    author='Dolibarr MCP Team',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='dolibarr mcp erp api integration',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.8',
    install_requires=[
        'mcp>=1.0.0',
        'requests>=2.31.0',
        'aiohttp>=3.9.0',
        'pydantic>=2.5.0',
        'click>=8.1.0',
        'python-dotenv>=1.0.0',
        'typing-extensions>=4.8.0',
    ],
    entry_points={
        'console_scripts': [
            'dolibarr-mcp=dolibarr_mcp.cli:main',
        ],
    },
)
