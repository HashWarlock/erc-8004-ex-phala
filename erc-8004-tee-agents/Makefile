# ERC-8004 TEE Agents Makefile
# Simple commands for agent development and deployment

.PHONY: help install test deploy clean examples docs

# Default target
help:
	@echo "🤖 ERC-8004 TEE Agents"
	@echo "====================="
	@echo ""
	@echo "Quick Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make setup      - Interactive project setup"
	@echo "  make test       - Run all tests"
	@echo "  make deploy     - Deploy agent to Phala Cloud"
	@echo "  make examples   - Run example workflows"
	@echo ""
	@echo "Development:"
	@echo "  make lint       - Code linting"
	@echo "  make format     - Format code"
	@echo "  make docs       - Generate documentation"
	@echo "  make clean      - Clean build artifacts"

# Installation and Setup
install:
	@echo "📦 Installing ERC-8004 TEE Agents..."
	pip install -e .
	@echo "✅ Installation complete!"

install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -e .[dev]
	@echo "✅ Dev installation complete!"

install-ai:
	@echo "🧠 Installing AI dependencies..."
	pip install -e .[ai]
	@echo "✅ AI installation complete!"

setup:
	@echo "🚀 Starting interactive setup..."
	python scripts/quick_setup.py

# Testing
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

test-unit:
	@echo "🔬 Running unit tests..."
	pytest tests/unit/ -v

test-integration:
	@echo "🔗 Running integration tests..."
	pytest tests/integration/ -v

test-e2e:
	@echo "🎯 Running end-to-end tests..."
	pytest tests/e2e/ -v

# Deployment
deploy:
	@echo "🚀 Deploying agent..."
	python scripts/deploy_agent.py

register:
	@echo "📝 Registering agent with ERC-8004..."
	python scripts/register_agent.py

# Examples
examples:
	@echo "📚 Running examples..."
	@echo "1. Basic workflow..."
	cd examples/basic_workflow && python run.py
	@echo ""
	@echo "2. AI-enhanced agent..."
	cd examples/ai_enhanced && python run.py

example-basic:
	@echo "🏃 Running basic example..."
	cd examples/basic_workflow && python run.py

example-ai:
	@echo "🧠 Running AI-enhanced example..."
	cd examples/ai_enhanced && python run.py

# Development Tools
lint:
	@echo "🔍 Linting code..."
	flake8 src/ tests/ examples/ || true
	pylint src/ || true

format:
	@echo "✨ Formatting code..."
	black src/ tests/ examples/ || true
	isort src/ tests/ examples/ || true

type-check:
	@echo "🔎 Type checking..."
	mypy src/ || true

# Documentation
docs:
	@echo "📖 Generating documentation..."
	@mkdir -p docs/_build
	@echo "Documentation generation not yet configured"

docs-serve:
	@echo "🌐 Serving documentation..."
	cd docs && python -m http.server 8080

# Utilities
generate-keys:
	@echo "🔑 Generating TEE keys..."
	python scripts/generate_keys.py

check-deployment:
	@echo "🔍 Checking deployment status..."
	@echo "Not yet implemented"

# Cleanup
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete

# Environment Management
env-create:
	@echo "🌍 Creating virtual environment..."
	python -m venv venv
	@echo "Activate with: source venv/bin/activate"

env-requirements:
	@echo "📋 Updating requirements.txt..."
	pip freeze > requirements.txt

# Quick Development Workflow
dev: install-dev lint test
	@echo "✅ Development workflow complete!"

# Production Checks
pre-deploy: lint type-check test
	@echo "✅ Pre-deployment checks passed!"

# Help for specific components
help-agents:
	@echo "🤖 Agent Development Help"
	@echo "========================"
	@echo "Agent types: server, validator, client, custom"
	@echo "Create new agent: make setup"
	@echo "Test agent: make test"

help-tee:
	@echo "🔐 TEE Integration Help"
	@echo "======================="
	@echo "Generate keys: make generate-keys"
	@echo "TEE docs: https://docs.phala.network"

help-registry:
	@echo "📝 Registry Integration Help"
	@echo "==========================="
	@echo "Register agent: make register"
	@echo "Registry docs: https://eips.ethereum.org/EIPS/eip-8004"