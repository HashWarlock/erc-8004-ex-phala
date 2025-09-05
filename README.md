# ERC-8004 Trustless Agents Example

**A complete demonstration of the [ERC-8004 Trustless Agents](https://eips.ethereum.org/EIPS/eip-8004) standard with AI Agents.**

This example showcases how AI agents can interact trustlessly across organizational boundaries using the [ERC-8004 registry system](https://github.com/ChaosChain/trustless-agents-erc-ri), demonstrating the future of decentralized AI collaboration.

## What This Example Demonstrates

- **✅ ERC-8004 Registry Contracts**: Identity, Reputation, and Validation registries
- **✅ AI Agents**: Using CrewAI for sophisticated market analysis and validation
- **✅ Trustless Interactions**: Agents discover, validate, and provide feedback without pre-existing trust
- **✅ Complete Audit Trail**: Full blockchain-based accountability and transparency
- **✅ Multi-Agent Workflows**: Collaborative AI systems working together

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Server Agent  │    │ Validator Agent │    │  Client Agent   │
│    (Alice)      │    │     (Bob)       │    │   (Charlie)     │
│                 │    │                 │    │                 │
│ • Market        │    │ • Valdidation   │    │ • Feedback      │
│   Analysis      │                      │    │   Authorization │
│ • Multi-agent   │    │ • Quality       │    │ • Reputation    │
│   workflows     │    │   Assessment    │    │   Management    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │  ERC-8004 Registries│
                    │                     │
                    │ • Identity Registry │
                    │ • Reputation Registry│
                    │ • Validation Registry│
                    └─────────────────────┘
```

## Quick Start

### Prerequisites

1. **Python 3.8+** with pip
2. **Node.js 16+** with npm (for Foundry)
3. **Foundry** (for smart contracts)

### Installation

1. **Clone and setup the example:**
   ```bash
   git clone https://github.com/chaoschain/erc-8004-example.git
   cd erc-8004-example
   
   # Option 1: Automated setup (recommended)
   ./setup.sh
   
   # Option 2: Manual setup
   pip install -r requirements.txt
   curl -L https://foundry.paradigm.xyz | bash
   foundryup
   ```

2. **Compile the smart contracts:**
   ```bash
   cd contracts
   forge install
   forge build
   cd ..
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start a local blockchain (optional):**
   ```bash
   # In a separate terminal
   anvil
   ```

### Run the Demo

```bash
python demo.py
```

## What Happens in the Demo

### Step 1: Contract Deployment
- Deploys the three ERC-8004 registry contracts
- Creates a complete trustless infrastructure

### Step 2: Agent Initialization
- **Alice (Server Agent)**: Market analysis service 
- **Bob (Validator Agent)**: Analysis validation service   
- **Charlie (Client Agent)**: Feedback and reputation management

### Step 3: Agent Registration
- All agents register with the Identity Registry
- Receive unique on-chain identities and agent IDs

### Step 4: Market Analysis Workflow
- Alice performs comprehensive BTC market analysis 
- Multi-agent workflow with analyst and reviewer roles
- Generates structured analysis with recommendations

### Step 5: Validation Request
- Alice submits her analysis for validation by Bob
- Creates cryptographic hash of the work
- Stores analysis data for validator access

### Step 6: AI-Powered Validation
- Bob validates Alice's analysis 
- Multi-agent validation with validator and QA specialist roles
- Generates validation score and detailed feedback

### Step 7: Validation Response
- Bob submits validation score (0-100) on-chain
- Creates permanent, immutable validation record

### Step 8: Feedback Authorization
- Charlie authorizes feedback for Alice's services
- Enables reputation building and trust networks

### Step 9: Audit Trail
- Complete blockchain-based audit trail
- Full transparency and accountability

## AI Agent Details

### Server Agent (Alice)
- **Role**: Market Analysis Service Provider
- **Capabilities**:
  - Senior Market Analyst for trend identification
  - Risk Assessment Specialist for validation
  - Structured analysis with confidence scores
  - Professional reporting standards

### Validator Agent (Bob)
- **Role**: Analysis Validation Service
- **Capabilities**:
  - Senior Analysis Validator for methodology review
  - Quality Assurance Specialist for final assessment
  - Comprehensive scoring (0-100)
  - Detailed feedback and improvement recommendations

## Project Structure

```
erc-8004-example/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment configuration template
├── demo.py                  # Main demonstration script
├── setup.sh                 # Automated setup script
├── SUMMARY.md               # Project summary
├── ERC-XXXX Trustless Agents v0.3.md  # ERC specification
│
├── contracts/               # Smart contracts
│   ├── src/                # Contract source code
│   │   ├── IdentityRegistry.sol
│   │   ├── ReputationRegistry.sol
│   │   ├── ValidationRegistry.sol
│   │   └── interfaces/     # Contract interfaces
│   ├── out/                # Compiled artifacts (ABIs)
│   ├── script/             # Deployment scripts
│   └── foundry.toml        # Foundry configuration
│
├── agents/                  # AI agent implementations
│   ├── __init__.py
│   ├── base_agent.py       # Base ERC-8004 agent class
│   ├── server_agent.py     # Market analysis server agent
│   └── validator_agent.py  # Analysis validation agent
│
├── scripts/                # Utility scripts
│   └── deploy.py           # Contract deployment script
├── data/                   # Generated analysis data (created at runtime)
└── validations/            # Generated validation data (created at runtime)
```

## Configuration

### Environment Variables (.env)

```bash
# Blockchain Configuration
RPC_URL=http://127.0.0.1:8545        # Local Anvil
PRIVATE_KEY=0x0000000000000000000000000000000000000000000000000000000000000000
CHAIN_ID=31337

# Agent Domains (optional)
AGENT_DOMAIN_ALICE=alice.example.com
AGENT_DOMAIN_BOB=bob.example.com

# AI Configuration (optional - for enhanced AI features)
# The demo works without these, using fallback analysis
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Network Support

The example works with any EVM-compatible network:

- **Local Development**: Anvil/Hardhat (default)
- **Testnets**: Sepolia, Goerli, Base Sepolia
- **Mainnets**: Ethereum, Base, Arbitrum, Optimism

Simply update the `RPC_URL` and `CHAIN_ID` in your `.env` file.

## Learning Outcomes

After running this example, you'll understand:

1. **ERC-8004 Standard**: How trustless agent interactions work
2. **Registry Architecture**: Identity, reputation, and validation systems
3. **Blockchain Integration**: Smart contract interaction patterns
4. **Trust Models**: How agents build reputation without pre-existing relationships

## Key Features Demonstrated

### Trust Models
- **Identity Registry**: Sovereign, portable agent identities
- **Reputation Registry**: Decentralized feedback and rating systems
- **Validation Registry**: Cryptoeconomic validation mechanisms

### AI Capabilities
- **Multi-Agent Workflows**: Collaborative AI systems
- **Structured Analysis**: Professional-grade market analysis
- **Quality Validation**: AI-powered validation and scoring
- **Continuous Learning**: Agents improve through feedback

### Blockchain Integration
- **Smart Contract Interaction**: Seamless Web3 integration
- **Event Monitoring**: Real-time blockchain event handling
- **Gas Optimization**: Efficient transaction patterns
- **Multi-Network Support**: Works across EVM chains

## Extending the Example

### Adding New Agent Types

1. **Create a new agent class** inheriting from `ERC8004BaseAgent`
2. **Implement AI workflows** for your specific use case
3. **Define trust models** your agent supports
4. **Update the demo script** to include your agent

### Integrating with Real APIs

1. **Replace mock data** in `MarketAnalysisTool` with real API calls
2. **Add authentication** for external services
3. **Implement error handling** for network failures
4. **Add rate limiting** for API usage

### Deploying to Production

1. **Use secure key management** (not hardcoded private keys)
2. **Deploy to testnets first** for validation
3. **Implement proper monitoring** and logging
4. **Add comprehensive error handling**

## Contributing

This example is designed to be educational and extensible. Contributions are welcome:

1. **Bug fixes** and improvements
2. **New agent types** and use cases
3. **Additional trust models** and validation methods
4. **Documentation** and tutorials

## Additional Resources

- **ERC-8004 Specification**: https://eips.ethereum.org/EIPS/eip-8004
- **CrewAI Documentation**: https://docs.crewai.com/
- **A2A Protocol**: https://a2a-protocol.org/
- **Foundry Book**: https://book.getfoundry.sh/

## Important Notes

- **Demo Purpose**: This is an educational example, not production-ready code
- **Security**: Use proper key management in production environments
- **Gas Costs**: Monitor transaction costs on mainnet deployments
- **AI Functionality**: Demo works fully without API keys using fallback analysis
  - With API keys: Full AI-powered analysis via CrewAI + LLMs
  - Without API keys: Intelligent fallback analysis (still demonstrates all ERC-8004 features)
- **Network Requirements**: Requires a running blockchain (Anvil recommended for local testing)

## Success Metrics

When you run this example successfully, you'll see:

- ✅ All contracts deployed and verified
- ✅ Three agents registered with unique IDs (Alice: Server, Bob: Validator, Charlie: Client)
- ✅ Complete market analysis generated by AI (BTC analysis with trend, support/resistance levels)
- ✅ Professional validation with scoring (96-100/100 validation scores)
- ✅ Full blockchain audit trail with transaction hashes
- ✅ Trustless agent interactions demonstrated across 7 steps

**Expected Output**: The demo runs through all 7 steps, showing real multi-agent workflows performing market analysis and validation, even without external API keys (using intelligent fallback analysis).

This example proves that sophisticated AI agents can work together trustlessly, laying the foundation for a decentralized agent economy!

---

**Built with ❤️ for the ERC-8004 Trustless Agents standard** 