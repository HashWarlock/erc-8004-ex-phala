"""
Setup configuration for ERC-8004 TEE Agents SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="erc-8004-tee-agents",
    version="0.1.0",
    author="ERC-8004 Contributors",
    author_email="contact@erc8004.dev",
    description="Streamlined SDK for building trustless TEE agents with ERC-8004",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/erc-8004-tee-agents",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "web3>=6.0.0",
        "eth-account>=0.8.0",
        "python-dotenv>=1.0.0",
        "dstack-sdk>=0.2.0",
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.5.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "eth-utils>=2.2.0",
    ],
    extras_require={
        "ai": [
            "openai>=1.0.0",
            "anthropic>=0.3.0",
            "crewai>=0.1.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "erc8004-setup=scripts.quick_setup:main",
            "erc8004-deploy=scripts.deploy_agent:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)