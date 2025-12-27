"""
Setup script for Kirwada OSINT Tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="kirwada",
    version="1.0.0",
    author="Kirwada Team",
    author_email="your-email@example.com",
    description="An open-source intelligence gathering tool with multiple reconnaissance plugins",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kirwada",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Internet",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "dnspython>=2.2.0",
    ],
    extras_require={
        "full": [
            "python-whois>=0.8.0",
            "shodan>=1.31.0",
            "sherlock>=0.14.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kirwada=main:main",
        ],
    },
)
