# ERC-8004 TEE Agents - Examples

This directory contains example implementations demonstrating various features and use cases of the ERC-8004 TEE Agent SDK.

## Available Examples

### 1. Basic Workflow (`basic_workflow/`)
**Purpose**: Demonstrates fundamental 3-agent interactions

**Key Features**:
- Server, Validator, and Client agent setup
- Task processing workflow
- Validation mechanisms
- Feedback system

**Best For**: Understanding the core agent communication patterns

[Full Documentation](basic_workflow/README.md)

### 2. AI-Enhanced Agents (`ai_enhanced/`)
**Purpose**: Shows integration with AI/ML capabilities

**Key Features**:
- Multi-provider AI support (OpenAI, Anthropic, Google, etc.)
- Intelligent task processing
- AI-powered analysis and decision making
- Fallback mechanisms

**Best For**: Building intelligent, context-aware agents

[Full Documentation](ai_enhanced/README.md)

### 3. Custom Validation (`custom_validation/`)
**Purpose**: Implements domain-specific validation rules

**Key Features**:
- Financial data validation
- Security checks
- Compliance validation (GDPR, KYC/AML)
- Consensus mechanisms

**Best For**: Creating specialized validation logic for your domain

[Full Documentation](custom_validation/README.md)

## Quick Start

### Prerequisites

1. Python 3.8+
2. Node.js (for blockchain interactions)
3. Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd erc-8004-tee-agents

# Install dependencies
pip install -r requirements.txt

# Choose an example
cd examples/basic_workflow
```

### Running Examples

Each example can be run independently:

```bash
# Basic workflow
cd examples/basic_workflow
cp .env.example .env
python run.py

# AI-enhanced
cd examples/ai_enhanced
cp .env.example .env
# Add AI API keys to .env
python run.py

# Custom validation
cd examples/custom_validation
cp .env.example .env
python run.py
```

## Common Configuration

All examples share these configuration options:

### Network Settings
```env
RPC_URL=https://sepolia.base.org
CHAIN_ID=84532
```

### Registry Addresses (Base Sepolia)
```env
IDENTITY_REGISTRY_ADDRESS=0x000c5A70B7269c5eD4238DcC6576e598614d3f70
REPUTATION_REGISTRY_ADDRESS=0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde
VALIDATION_REGISTRY_ADDRESS=0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d
TEE_VERIFIER_ADDRESS=0x1b841e88ba786027f39ecf9Cd160176b22E3603c
```

### TEE Mode
```env
# Development (no TEE required)
USE_TEE_AUTH=false

# Production (requires TEE environment)
USE_TEE_AUTH=true
DSTACK_SIMULATOR_ENDPOINT=http://localhost:8090
```

## Development vs Production

### Development Mode
- `USE_TEE_AUTH=false` - No TEE required
- `SKIP_REGISTRATION=true` - Skip blockchain registration
- Uses test private keys
- Runs locally without hardware requirements

### Production Mode
- `USE_TEE_AUTH=true` - TEE authentication enabled
- `SKIP_REGISTRATION=false` - Full blockchain registration
- Keys derived from TEE
- Requires Phala Cloud or TEE simulator

## Example Comparison

| Feature | Basic Workflow | AI-Enhanced | Custom Validation |
|---------|---------------|-------------|-------------------|
| **Complexity** | Low | Medium | Medium-High |
| **External Dependencies** | None | AI API Keys | None |
| **Use Case** | Standard operations | Intelligent agents | Specialized validation |
| **Agent Types** | 3 (Server, Validator, Client) | 3 with AI plugins | 1 with multiple validators |
| **Best For** | Learning basics | Smart applications | Domain-specific needs |

## Creating Your Own Example

Use these examples as templates:

1. **Start with Basic Workflow** if you need standard agent interactions
2. **Extend AI-Enhanced** for intelligent processing capabilities
3. **Build on Custom Validation** for specialized business logic

### Template Structure

```python
#!/usr/bin/env python3
"""Your Example Description"""

import asyncio
from src.agent.base import AgentConfig, AgentRole
from src.templates.server_agent import ServerAgent

class YourCustomAgent(ServerAgent):
    """Your custom agent implementation."""

    async def process_task(self, task_data):
        # Your custom logic
        result = await super().process_task(task_data)
        # Additional processing
        return result

async def main():
    # Setup and run your example
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

## Combining Examples

You can combine features from different examples:

```python
# Combine AI and Custom Validation
from examples.ai_enhanced.run import AIEnhancedServerAgent
from examples.custom_validation.run import CustomValidatorAgent

class SmartValidatedAgent(AIEnhancedServerAgent):
    def __init__(self, config, registries):
        super().__init__(config, registries)
        self.custom_validator = CustomValidatorAgent(...)

    async def process_task(self, task_data):
        # AI-enhanced processing
        result = await super().process_task(task_data)

        # Custom validation
        validation = await self.custom_validator.validate_with_custom_rules(result)

        if validation['overall_valid']:
            return result
        else:
            raise ValidationError(validation['issues'])
```

## Testing Examples

### Unit Testing
```bash
# Run tests for specific example
cd examples/basic_workflow
python -m pytest tests/
```

### Integration Testing
```bash
# Test with local TEE simulator
docker run -p 8090:8090 phalanetwork/tee-simulator
export USE_TEE_AUTH=true
python run.py
```

### End-to-End Testing
```bash
# Deploy to testnet
export USE_TEE_AUTH=true
export SKIP_REGISTRATION=false
python run.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the right directory
   cd erc-8004-tee-agents
   pip install -e .
   ```

2. **Network Errors**
   ```bash
   # Check RPC endpoint
   curl https://sepolia.base.org
   ```

3. **TEE Errors**
   ```bash
   # Start simulator for testing
   docker run -p 8090:8090 phalanetwork/tee-simulator
   ```

### Debug Mode

Enable debug output:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Resources

### Documentation
- [Main README](../README.md)
- [API Reference](../docs/api_reference.md)
- [Deployment Guide](../docs/deployment_guide.md)

### External Links
- [ERC-8004 Standard](https://ethereum.org/en/developers/docs/standards/tokens/erc-8004/)
- [Phala Network](https://phala.network/)
- [Base Sepolia Testnet](https://docs.base.org/network-information)

## Contributing

To add a new example:

1. Create a new directory under `examples/`
2. Include:
   - `run.py` - Main implementation
   - `.env.example` - Configuration template
   - `README.md` - Documentation
   - `requirements.txt` - Additional dependencies (if any)

3. Follow the existing patterns for consistency
4. Test thoroughly in both development and TEE modes
5. Submit a pull request

## Support

For questions or issues:
- Check individual example READMEs
- Review the [main documentation](../README.md)
- Open an issue on GitHub
- Contact the development team

---

Happy building with ERC-8004 TEE Agents! 🚀