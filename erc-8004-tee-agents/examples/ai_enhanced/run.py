#!/usr/bin/env python3
"""
AI-Enhanced Agent Workflow Example

Demonstrates agents enhanced with AI capabilities using OpenAI/Anthropic
for intelligent task processing and decision making.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from src.agent.base import AgentConfig, AgentRole, RegistryAddresses
from src.templates.server_agent import ServerAgent
from src.templates.validator_agent import ValidatorAgent
from src.templates.client_agent import ClientAgent


class AIEnhancedServerAgent(ServerAgent):
    """Server agent enhanced with AI capabilities."""

    def __init__(self, config, registries):
        super().__init__(config, registries)
        self.setup_ai_capabilities()

    def setup_ai_capabilities(self):
        """Initialize AI components."""
        try:
            # Check if AI libraries are available
            import openai
            self.has_openai = bool(os.getenv('OPENAI_API_KEY'))
            if self.has_openai:
                openai.api_key = os.getenv('OPENAI_API_KEY')
                print("🧠 OpenAI capabilities enabled")
        except ImportError:
            self.has_openai = False

        try:
            import anthropic
            self.has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
            if self.has_anthropic:
                self.anthropic_client = anthropic.Anthropic(
                    api_key=os.getenv('ANTHROPIC_API_KEY')
                )
                print("🧠 Anthropic capabilities enabled")
        except ImportError:
            self.has_anthropic = False

        # Add AI plugin
        if self.has_openai or self.has_anthropic:
            self.add_plugin('ai_analyzer', AIAnalyzer(self))

    async def process_task(self, task_data):
        """Process task with AI enhancement."""
        result = await super().process_task(task_data)

        # Enhance with AI if available
        ai_plugin = self.get_plugin('ai_analyzer')
        if ai_plugin:
            ai_analysis = await ai_plugin.analyze(task_data, result)
            result['ai_enhanced'] = ai_analysis
            result['confidence'] = min(1.0, result.get('confidence', 0.5) + 0.2)

        return result


class AIAnalyzer:
    """AI analysis plugin for agents."""

    def __init__(self, agent):
        self.agent = agent

    async def analyze(self, task_data, initial_result):
        """Perform AI-enhanced analysis."""
        query = task_data.get('query', '')

        if not query:
            return {"status": "no_query"}

        # Try OpenAI first
        if hasattr(self.agent, 'has_openai') and self.agent.has_openai:
            return await self.analyze_with_openai(query, initial_result)

        # Fallback to Anthropic
        if hasattr(self.agent, 'has_anthropic') and self.agent.has_anthropic:
            return await self.analyze_with_anthropic(query, initial_result)

        # Fallback to mock AI
        return await self.mock_ai_analysis(query, initial_result)

    async def analyze_with_openai(self, query, initial_result):
        """Use OpenAI for analysis."""
        try:
            import openai

            prompt = f"""
            Analyze the following query and provide insights:
            Query: {query}
            Initial Analysis: {json.dumps(initial_result.get('analysis', {}), indent=2)}

            Provide:
            1. Key insights
            2. Risk factors
            3. Recommendations
            """

            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content

            return {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "analysis": ai_response,
                "enhanced": True
            }

        except Exception as e:
            print(f"⚠️  OpenAI analysis failed: {e}")
            return await self.mock_ai_analysis(query, initial_result)

    async def analyze_with_anthropic(self, query, initial_result):
        """Use Anthropic for analysis."""
        try:
            prompt = f"""
            Analyze the following query and provide insights:
            Query: {query}
            Initial Analysis: {json.dumps(initial_result.get('analysis', {}), indent=2)}

            Provide:
            1. Key insights
            2. Risk factors
            3. Recommendations
            """

            response = await asyncio.to_thread(
                self.agent.anthropic_client.messages.create,
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            ai_response = response.content[0].text

            return {
                "provider": "anthropic",
                "model": "claude-3-haiku",
                "analysis": ai_response,
                "enhanced": True
            }

        except Exception as e:
            print(f"⚠️  Anthropic analysis failed: {e}")
            return await self.mock_ai_analysis(query, initial_result)

    async def mock_ai_analysis(self, query, initial_result):
        """Provide mock AI analysis for demo purposes."""
        await asyncio.sleep(0.5)  # Simulate processing time

        return {
            "provider": "mock",
            "model": "demo-ai",
            "analysis": {
                "insights": [
                    f"The query '{query[:50]}...' shows interest in detailed analysis",
                    "Market conditions appear favorable based on initial metrics",
                    "Further validation recommended for high-confidence decisions"
                ],
                "risk_factors": [
                    "Market volatility remains a concern",
                    "Data freshness should be verified",
                    "External factors may impact accuracy"
                ],
                "recommendations": [
                    "Consider multiple data sources for validation",
                    "Implement risk management strategies",
                    "Monitor trends over extended timeframes"
                ],
                "confidence_boost": 0.15
            },
            "enhanced": True
        }


class AIEnhancedWorkflowDemo:
    """Orchestrates AI-enhanced agent workflow demonstration."""

    def __init__(self):
        """Initialize the demo."""
        load_dotenv()
        self.agents = {}

    async def setup_agents(self):
        """Initialize AI-enhanced agents."""
        print("🚀 Setting up AI-Enhanced Agent Workflow")
        print("=" * 50)

        # Common configuration
        registries = RegistryAddresses(
            identity=os.getenv('IDENTITY_REGISTRY_ADDRESS', '0x000c5A70B7269c5eD4238DcC6576e598614d3f70'),
            reputation=os.getenv('REPUTATION_REGISTRY_ADDRESS', '0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde'),
            validation=os.getenv('VALIDATION_REGISTRY_ADDRESS', '0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d'),
            tee_verifier=os.getenv('TEE_VERIFIER_ADDRESS', '0x1b841e88ba786027f39ecf9Cd160176b22E3603c')
        )

        use_tee = os.getenv('USE_TEE_AUTH', 'false').lower() == 'true'
        rpc_url = os.getenv('RPC_URL', 'https://sepolia.base.org')
        chain_id = int(os.getenv('CHAIN_ID', '84532'))

        # Initialize AI-Enhanced Server
        print("\n🧠 Initializing AI-Enhanced Server Agent...")
        server_config = AgentConfig(
            domain="ai-server.example.com",
            salt="ai-server-salt",
            role=AgentRole.SERVER,
            rpc_url=rpc_url,
            chain_id=chain_id,
            use_tee_auth=use_tee,
            private_key=os.getenv('SERVER_PRIVATE_KEY') if not use_tee else None
        )
        self.agents['server'] = AIEnhancedServerAgent(server_config, registries)

        # Regular Validator
        print("\n🔍 Initializing Validator Agent...")
        validator_config = AgentConfig(
            domain="validator.example.com",
            salt="validator-salt",
            role=AgentRole.VALIDATOR,
            rpc_url=rpc_url,
            chain_id=chain_id,
            use_tee_auth=use_tee,
            private_key=os.getenv('VALIDATOR_PRIVATE_KEY') if not use_tee else None
        )
        self.agents['validator'] = ValidatorAgent(validator_config, registries)

        # Regular Client
        print("\n📝 Initializing Client Agent...")
        client_config = AgentConfig(
            domain="client.example.com",
            salt="client-salt",
            role=AgentRole.CLIENT,
            rpc_url=rpc_url,
            chain_id=chain_id,
            use_tee_auth=use_tee,
            private_key=os.getenv('CLIENT_PRIVATE_KEY') if not use_tee else None
        )
        self.agents['client'] = ClientAgent(client_config, registries)

        print("\n✅ All agents initialized!")

    async def demonstrate_ai_workflow(self):
        """Run AI-enhanced workflow demonstration."""
        print("\n" + "=" * 50)
        print("🎭 Starting AI-Enhanced Workflow")
        print("=" * 50)

        # Complex query requiring AI analysis
        print("\n📤 Step 1: Client requests complex analysis")
        complex_request = {
            'task_id': 'ai_demo_001',
            'query': 'Analyze the potential impact of quantum computing on blockchain security over the next 5 years, considering current technological progress and adoption rates',
            'data': {
                'domain': 'blockchain_security',
                'timeframe': '5_years',
                'factors': ['quantum_computing', 'cryptography', 'adoption'],
                'require_ai': True
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        # Server processes with AI enhancement
        server_result = await self.agents['server'].process_task(complex_request)

        print(f"✅ AI-Enhanced Server processed request")
        print(f"   Base confidence: {server_result.get('confidence', 0)}")

        if 'ai_enhanced' in server_result:
            ai_data = server_result['ai_enhanced']
            print(f"   AI Provider: {ai_data.get('provider', 'none')}")
            print(f"   AI Model: {ai_data.get('model', 'none')}")
            print(f"   Enhanced: {ai_data.get('enhanced', False)}")

            if ai_data.get('provider') == 'mock':
                insights = ai_data['analysis'].get('insights', [])
                if insights:
                    print("\n   🔍 AI Insights:")
                    for insight in insights[:2]:
                        print(f"      - {insight}")

        # Validation step
        print("\n🔍 Step 2: Validate AI-enhanced results")
        import hashlib
        result_json = json.dumps(server_result.get('analysis', {}), sort_keys=True)
        data_hash = hashlib.sha256(result_json.encode()).hexdigest()

        validation_request = {
            'request_id': 'val_ai_001',
            'data_hash': data_hash,
            'data': server_result,
            'validation_type': 'computation',
            'requester': 'ai_server'
        }

        validator_result = await self.agents['validator'].process_task(validation_request)
        print(f"✅ Validation complete: {'Valid' if validator_result.get('is_valid') else 'Invalid'}")

        # Intelligent feedback based on AI analysis
        print("\n⭐ Step 3: Submit intelligent feedback")

        # Determine rating based on AI enhancement and validation
        base_rating = 3
        if server_result.get('ai_enhanced', {}).get('enhanced'):
            base_rating += 1
        if validator_result.get('is_valid'):
            base_rating += 1

        feedback_request = {
            'task_type': 'feedback',
            'target_agent_id': 1,  # Mock ID
            'rating': min(5, base_rating),
            'comment': 'Excellent AI-enhanced analysis with validated results',
            'data': {
                'service_type': 'ai_analysis',
                'ai_quality': 'high' if base_rating >= 4 else 'medium'
            }
        }

        feedback_result = await self.agents['client'].process_task(feedback_request)
        print(f"✅ Intelligent feedback submitted: Rating {feedback_request['rating']}/5")

        # Summary
        print("\n" + "=" * 50)
        print("📊 AI Workflow Summary")
        print("=" * 50)

        summary = {
            'workflow': 'ai_enhanced',
            'timestamp': datetime.utcnow().isoformat(),
            'enhancements': {
                'ai_provider': server_result.get('ai_enhanced', {}).get('provider', 'none'),
                'ai_model': server_result.get('ai_enhanced', {}).get('model', 'none'),
                'confidence_boost': server_result.get('confidence', 0) - 0.8
            },
            'results': {
                'ai_enhanced': bool(server_result.get('ai_enhanced')),
                'validation_passed': validator_result.get('is_valid', False),
                'final_rating': feedback_request['rating']
            }
        }

        print(json.dumps(summary, indent=2))
        return summary


async def main():
    """Run the AI-enhanced workflow demonstration."""
    demo = AIEnhancedWorkflowDemo()

    try:
        await demo.setup_agents()
        result = await demo.demonstrate_ai_workflow()
        print("\n✨ AI-enhanced workflow completed successfully!")

    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║  ERC-8004 TEE Agents - AI Enhanced      ║
    ║                                          ║
    ║  Intelligent Agents with AI/ML          ║
    ╚══════════════════════════════════════════╝
    """)

    asyncio.run(main())