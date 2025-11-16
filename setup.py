#!/usr/bin/env python3
"""
Setup script for PathForm Python package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="pathform",
    version="0.1.0",
    description="A token-cheap, LLM-friendly text format that round-trips cleanly to JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mehmet T. AKALIN",
    author_email="makalin@example.com",
    url="https://github.com/makalin/pathform",
    py_modules=["pathform"],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "pathform2json=pathform2json:main",
            "json2pathform=json2pathform:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    keywords="pathform json parser llm ai format text-format structured-data",
    project_urls={
        "Bug Reports": "https://github.com/makalin/pathform/issues",
        "Source": "https://github.com/makalin/pathalin/pathform",
    },
)

