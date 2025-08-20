#!/bin/bash

# ERC-8004 Example Setup Script
# This script automates the setup process for the ERC-8004 example

set -e  # Exit on any error

echo "🚀 ERC-8004 Trustless Agents Example Setup"
echo "=========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 found"

# Install Python dependencies
echo
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if Foundry is installed
if ! command -v forge &> /dev/null; then
    echo
    echo "🔧 Foundry not found. Installing Foundry..."
    curl -L https://foundry.paradigm.xyz | bash
    source ~/.bashrc
    foundryup
else
    echo "✅ Foundry found: $(forge --version | head -n1)"
fi

# Setup contracts
echo
echo "🏗️  Setting up smart contracts..."
cd contracts

# Install Foundry dependencies
if [ ! -d "lib" ]; then
    echo "📦 Installing Foundry dependencies..."
    forge install
fi

# Compile contracts
echo "🔨 Compiling contracts..."
forge build

cd ..

# Setup environment
if [ ! -f ".env" ]; then
    echo
    echo "⚙️  Setting up environment configuration..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "📝 Please edit .env file with your configuration before running the demo"
else
    echo "✅ .env file already exists"
fi

# Create data directories
mkdir -p data validations

echo
echo "🎉 Setup completed successfully!"
echo
echo "Next steps:"
echo "1. Edit .env file with your configuration (RPC_URL, PRIVATE_KEY, etc.)"
echo "2. Start a local blockchain: anvil (in a separate terminal)"
echo "3. Run the demo: python demo.py"
echo
echo "For more information, see README.md" 