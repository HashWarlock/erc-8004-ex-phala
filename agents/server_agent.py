"""
Server Agent - Market Analysis Service

This agent demonstrates a Server Agent role in the ERC-8004 ecosystem.
It uses CrewAI to perform market analysis tasks and submits its work
for validation through the ERC-8004 registries.
"""

import hashlib
import json
from typing import Dict, Any
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from .base_agent import ERC8004BaseAgent

class MarketAnalysisInput(BaseModel):
    """Input model for market analysis"""
    symbol: str = Field(description="Trading symbol to analyze (e.g., 'BTC', 'ETH')")
    timeframe: str = Field(description="Analysis timeframe (e.g., '1d', '1w', '1m')")
    
class MarketAnalysisTool(BaseTool):
    """Tool for performing market analysis"""
    name: str = "market_analysis"
    description: str = "Analyzes market data for a given symbol and timeframe"
    args_schema: type[BaseModel] = MarketAnalysisInput
    
    def _run(self, symbol: str, timeframe: str) -> str:
        """
        Perform market analysis (simplified for demo)
        In a real implementation, this would connect to market data APIs
        """
        # Simulate market analysis
        analysis = {
            "symbol": symbol,
            "timeframe": timeframe,
            "price_trend": "bullish" if hash(symbol) % 2 == 0 else "bearish",
            "confidence": 85,
            "key_levels": {
                "support": 45000 if symbol == "BTC" else 2800,
                "resistance": 52000 if symbol == "BTC" else 3200
            },
            "recommendation": "BUY" if hash(symbol) % 2 == 0 else "HOLD",
            "risk_level": "medium"
        }
        
        return json.dumps(analysis, indent=2)

class ServerAgent(ERC8004BaseAgent):
    """
    Server Agent that provides market analysis services
    """
    
    def __init__(self, agent_domain: str, private_key: str):
        """Initialize the Server Agent"""
        super().__init__(agent_domain, private_key)
        
        # Initialize CrewAI components
        self._setup_crew()
        
        print(f"🤖 Server Agent initialized")
        print(f"   Domain: {self.agent_domain}")
        print(f"   Address: {self.address}")
    
    def _setup_crew(self):
        """Setup the CrewAI crew for market analysis"""
        
        # Create the market analysis tool
        self.market_tool = MarketAnalysisTool()
        
        # Define the analyst agent
        self.analyst = Agent(
            role="Senior Market Analyst",
            goal="Provide accurate and insightful market analysis for cryptocurrency assets",
            backstory="""You are a seasoned market analyst with 10+ years of experience 
            in cryptocurrency markets. You excel at identifying trends, key price levels, 
            and providing actionable trading recommendations based on technical analysis.""",
            tools=[self.market_tool],
            verbose=True,
            allow_delegation=False
        )
        
        # Define the reviewer agent
        self.reviewer = Agent(
            role="Risk Assessment Specialist",
            goal="Review and validate market analysis for accuracy and risk assessment",
            backstory="""You are a risk management expert who specializes in reviewing 
            market analysis reports. Your job is to ensure the analysis is sound, 
            well-reasoned, and includes appropriate risk warnings.""",
            verbose=True,
            allow_delegation=False
        )
    
    def perform_market_analysis(self, symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
        """
        Perform comprehensive market analysis using CrewAI
        
        Args:
            symbol: Trading symbol to analyze
            timeframe: Analysis timeframe
            
        Returns:
            Analysis results with metadata
        """
        print(f"📊 Starting market analysis for {symbol} ({timeframe})")
        
        # Create analysis task
        analysis_task = Task(
            description=f"""
            Perform a comprehensive market analysis for {symbol} with the following requirements:
            
            1. Analyze the current price trend and momentum
            2. Identify key support and resistance levels
            3. Provide a clear trading recommendation (BUY/SELL/HOLD)
            4. Assess the risk level of the current market conditions
            5. Include confidence level in your analysis
            
            Use the market_analysis tool to gather the necessary data.
            Present your findings in a clear, structured format.
            """,
            agent=self.analyst,
            expected_output="A detailed market analysis report with trend assessment, key levels, recommendation, and risk evaluation"
        )
        
        # Create review task
        review_task = Task(
            description=f"""
            Review the market analysis report for {symbol} and provide:
            
            1. Validation of the analysis methodology
            2. Assessment of risk factors and warnings
            3. Confirmation or adjustment of the confidence level
            4. Final recommendation with risk disclaimer
            
            Ensure the analysis meets professional standards and includes appropriate risk warnings.
            """,
            agent=self.reviewer,
            expected_output="A reviewed and validated market analysis with risk assessment and final recommendations"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.analyst, self.reviewer],
            tasks=[analysis_task, review_task],
            verbose=True
        )
        
        # Execute the analysis
        try:
            result = crew.kickoff()
        except Exception as e:
            # Fallback to mock analysis if LLM fails
            print(f"⚠️  LLM analysis failed ({str(e)[:50]}...), using fallback analysis")
            result = self._create_fallback_analysis(symbol, timeframe)
        
        # Prepare the final analysis package
        analysis_package = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": self.w3.eth.get_block('latest')['timestamp'],
            "agent_id": self.agent_id,
            "agent_domain": self.agent_domain,
            "analysis": str(result),
            "metadata": {
                "crew_agents": len(crew.agents),
                "tasks_completed": len(crew.tasks),
                "analysis_method": "CrewAI Multi-Agent Analysis"
            }
        }
        
        print(f"✅ Market analysis completed for {symbol}")
        return analysis_package
    
    def submit_work_for_validation(self, analysis_package: Dict[str, Any], validator_agent_id: int) -> str:
        """
        Submit analysis work for validation through ERC-8004
        
        Args:
            analysis_package: The completed analysis
            validator_agent_id: ID of the validator agent
            
        Returns:
            Transaction hash of the validation request
        """
        # Create a hash of the analysis package
        analysis_json = json.dumps(analysis_package, sort_keys=True)
        data_hash = hashlib.sha256(analysis_json.encode()).digest()
        
        print(f"📤 Submitting work for validation")
        print(f"   Data hash: {data_hash.hex()}")
        print(f"   Validator: Agent {validator_agent_id}")
        
        # Store the analysis package for the validator to retrieve
        # In a real implementation, this would be stored on IPFS or similar
        self._store_analysis_package(data_hash.hex(), analysis_package)
        
        # Request validation through ERC-8004
        tx_hash = self.request_validation(validator_agent_id, data_hash)
        
        return tx_hash
    
    def _create_fallback_analysis(self, symbol: str, timeframe: str) -> str:
        """Create a fallback analysis when LLM is not available"""
        analysis = {
            "symbol": symbol,
            "timeframe": timeframe,
            "trend": "bullish" if hash(symbol) % 2 == 0 else "bearish",
            "confidence": 75,
            "support_level": 45000 if symbol == "BTC" else 2800,
            "resistance_level": 52000 if symbol == "BTC" else 3200,
            "recommendation": "BUY" if hash(symbol) % 2 == 0 else "HOLD",
            "risk_level": "medium",
            "analysis_note": "This is a fallback analysis generated without LLM. For full AI-powered analysis, please configure OPENAI_API_KEY."
        }
        
        return f"""
# Market Analysis Report for {symbol}

## Executive Summary
Based on technical analysis of {symbol} over the {timeframe} timeframe, the market shows a **{analysis['trend']}** trend with **{analysis['risk_level']}** risk levels.

## Key Findings
- **Current Trend**: {analysis['trend'].title()}
- **Support Level**: ${analysis['support_level']:,}
- **Resistance Level**: ${analysis['resistance_level']:,}
- **Confidence Level**: {analysis['confidence']}%

## Recommendation
**{analysis['recommendation']}** - {analysis['analysis_note']}

## Risk Assessment
The current market conditions present {analysis['risk_level']} risk levels. Traders should exercise appropriate caution and position sizing.

*Note: This analysis was generated using fallback logic. For AI-powered analysis with CrewAI, please configure your OpenAI API key.*
"""

    def _store_analysis_package(self, data_hash: str, analysis_package: Dict[str, Any]):
        """Store analysis package for validator retrieval (simplified for demo)"""
        # In production, this would use IPFS or decentralized storage
        import os
        os.makedirs("data", exist_ok=True)
        
        with open(f"data/{data_hash}.json", 'w') as f:
            json.dump(analysis_package, f, indent=2)
        
        print(f"💾 Analysis package stored: data/{data_hash}.json")
    
    def get_trust_models(self) -> list:
        """Return supported trust models for this agent"""
        return ["feedback", "inference-validation"]
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Generate AgentCard following A2A specification"""
        return {
            "agentId": self.agent_id,
            "name": "Market Analysis Server Agent",
            "description": "Provides comprehensive cryptocurrency market analysis using AI",
            "version": "1.0.0",
            "skills": [
                {
                    "skillId": "market-analysis",
                    "name": "Market Analysis",
                    "description": "Comprehensive cryptocurrency market analysis with trend identification and trading recommendations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Trading symbol"},
                            "timeframe": {"type": "string", "description": "Analysis timeframe"}
                        },
                        "required": ["symbol"]
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "analysis": {"type": "string"},
                            "recommendation": {"type": "string"},
                            "confidence": {"type": "number"}
                        }
                    }
                }
            ],
            "trustModels": self.get_trust_models(),
            "registrations": [
                {
                    "agentId": self.agent_id,
                    "agentAddress": f"eip155:{self.w3.eth.chain_id}:{self.address}",
                    "signature": "0x..."  # Would be actual signature in production
                }
            ]
        } 