#!/usr/bin/env python3
"""
Setup script for Financial Valuation Engine
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="financial-valuation-engine",
    version="2.0.0",
    author="Pranay Upreti",
    author_email="pranay@example.com",
    description="A comprehensive financial valuation platform with advanced DCF modeling",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/financial-valuation-engine",
    packages=find_packages(include=["backend*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "valuation-api=backend.main:app",
        ],
    },
    include_package_data=True,
    package_data={
        "backend": ["py.typed"],
    },
    zip_safe=False,
) 