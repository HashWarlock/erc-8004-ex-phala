# ERC-8004 Trustless Agents - Documentation

## Overview
This directory contains comprehensive documentation for the ERC-8004 Trustless Agents implementation with Phala Cloud TEE integration.

## Documentation Structure

### 📚 Core Documentation

- **[Architecture Guide](ARCHITECTURE.md)** - System architecture, TEE integration, dual-mode operation
- **[API Reference](API_REFERENCE.md)** - Complete API documentation with TEE endpoints
- **[Deployment Guide](DEPLOYMENT.md)** - Local and Phala Cloud deployment instructions
- **[Testing Guide](TESTING.md)** - Testing with TEE mode and traditional mode

### 🔧 Development Guides

- **[Development Setup](DEVELOPMENT.md)** - Flox environment setup and development workflow
- **[Developer Tasks](../TODO.md)** - Sprint tasks and setup checklists for developers
- **[Contributing](CONTRIBUTING.md)** - Guidelines for contributors

### 🚀 Quick Start

```bash
# Install Flox
curl -fsSL https://downloads.flox.dev/by/flox/sh | sh

# Clone and setup
git clone <repository>
cd erc-8004-ex-phala
flox activate
cp .env.example .env

# Start development
flox activate -- make anvil    # Terminal 1
flox activate -- make deploy   # Terminal 2
flox activate -- ./run_demo.sh # Terminal 3
```

## Quick Links

- [Project README](../README.md)
- [API Server](../api/)
- [Agent Implementations](../agents/)
- [Smart Contracts](../contracts/)
- [Tests](../tests/)

## Key Features

- **Dual Mode Operation**: Supports both TEE-based and traditional key authentication
- **Automatic Wallet Funding**: TEE agents auto-funded during initialization
- **Phala Cloud Integration**: Deterministic key derivation via TEE
- **Complete Test Suite**: Unit, integration, and E2E tests included
- **Flox Environment**: All dependencies managed through Flox

## Documentation Status

Last Updated: September 2025
Version: 1.0.0
TEE Mode: Fully Implemented