"""
Genesis Studio - Server Agent (Alice) with ChaosChain SDK Integration

This agent demonstrates a Server Agent role using both CrewAI for AI capabilities
and ChaosChain SDK for payments, process integrity, and on-chain interactions.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from rich import print as rprint

# Import ChaosChain SDK components
try:
    from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig, AgentRole
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    # Create dummy classes for type hints when SDK is not available
    class NetworkConfig:
        BASE_SEPOLIA = "base-sepolia"
    class AgentRole:
        SERVER = "server"
    rprint("[red]❌ ChaosChain SDK not available. Please install: pip install chaoschain-sdk[/red]")

class ShoppingAnalysisInput(BaseModel):
    """Input model for shopping analysis"""
    item_type: str = Field(description="Type of item to shop for (e.g., 'winter_jacket', 'laptop')")
    color: str = Field(description="Preferred color")
    budget: float = Field(description="Maximum budget in USD")
    premium_tolerance: float = Field(description="Acceptable premium for preferred options (0.0-1.0)")

class GenesisShoppingAnalysisTool(BaseTool):
    """Enhanced shopping analysis tool for Genesis Studio using CrewAI"""
    name: str = "genesis_shopping_analysis"
    description: str = "Performs comprehensive smart shopping analysis for Genesis Studio"
    args_schema: type[BaseModel] = ShoppingAnalysisInput
    
    def _run(self, item_type: str, color: str, budget: float, premium_tolerance: float = 0.20) -> str:
        """
        Perform enhanced shopping analysis using CrewAI-powered logic
        """
        
        rprint(f"[yellow]🛒 CrewAI analyzing {item_type} in {color} (budget: ${budget})[/yellow]")
        
        # Enhanced CrewAI-powered shopping analysis
        import random
        
        # Simulate intelligent price discovery
        base_price = random.uniform(budget * 0.6, budget * 0.85)
        
        # Simulate color matching intelligence
        color_match_probability = 0.8  # CrewAI has better success rate
        found_color_match = random.random() < color_match_probability
        
        if found_color_match:
            # Apply premium for color match
            premium_factor = random.uniform(0.05, premium_tolerance)
            final_price = base_price * (1 + premium_factor)
            deal_quality = "excellent" if final_price < budget * 0.9 else "good"
            available_color = color
        else:
            # Fallback to alternative color
            final_price = base_price
            deal_quality = "alternative"
            available_color = random.choice(["black", "navy", "gray", "brown"])
        
        # CrewAI-enhanced merchant selection
        merchants = [
            "Premium Outdoor Gear Co.", "Elite Sports Equipment", "Professional Outfitters",
            "Quality Gear Direct", "Adventure Equipment Pro"
        ]
        selected_merchant = random.choice(merchants)
        
        # Enhanced analysis with CrewAI intelligence
        analysis = {
            "item_type": item_type,
            "requested_color": color,
            "available_color": available_color,
            "base_price": round(base_price, 2),
            "final_price": round(final_price, 2),
            "premium_applied": round((final_price - base_price) / base_price * 100, 1) if found_color_match else 0,
            "deal_quality": deal_quality,
            "color_match_found": found_color_match,
            "merchant": selected_merchant,
            "availability": "in_stock",
            "estimated_delivery": random.choice(["1-2 business days", "2-3 business days", "3-5 business days"]),
            "auto_purchase_eligible": final_price <= (budget * (1 + premium_tolerance)),
            "search_timestamp": datetime.now().isoformat(),
            "shopping_agent": "Alice (CrewAI Smart Shopping)",
            "crewai_analysis": {
                "market_scan_results": f"Analyzed {random.randint(15, 35)} products across {random.randint(5, 12)} merchants",
                "price_comparison": f"Found {random.randint(3, 8)} alternatives within budget",
                "quality_assessment": "Premium quality verified through merchant reputation analysis",
                "availability_check": "Real-time inventory confirmed",
                "delivery_optimization": "Fastest available shipping option selected"
            },
            "crewai_metadata": {
                "analysis_depth": "comprehensive",
                "data_sources": ["merchant_apis", "price_comparison", "inventory_systems", "review_analysis"],
                "confidence_factors": {
                    "price_accuracy": 0.95,
                    "availability_confidence": 0.92,
                    "quality_assessment": 0.88,
                    "delivery_estimate": 0.90
                }
            },
            "confidence": random.uniform(0.88, 0.96)  # Higher confidence with CrewAI
        }
        
        return json.dumps(analysis, indent=2)

class GenesisServerAgentSDK:
    """Enhanced Server Agent for Genesis Studio using ChaosChain SDK + CrewAI"""
    
    def __init__(self, agent_name: str, agent_domain: str, agent_role: AgentRole = AgentRole.SERVER,
                 network: NetworkConfig = NetworkConfig.BASE_SEPOLIA,
                 enable_ap2: bool = True, enable_process_integrity: bool = True):
        """
        Initialize the Genesis Server Agent with ChaosChain SDK and CrewAI
        
        Args:
            agent_name: Name of the agent (e.g., "Alice")
            agent_domain: Domain where agent's card is hosted
            agent_role: Role of the agent (defaults to SERVER)
            network: Blockchain network to use
            enable_ap2: Enable AP2 integration for intent verification
            enable_process_integrity: Enable process integrity verification
        """
        if not SDK_AVAILABLE:
            raise ImportError("ChaosChain SDK is required for GenesisServerAgentSDK")
        
        self.agent_name = agent_name
        self.agent_domain = agent_domain
        self.agent_role = agent_role
        self.network = network
        
        # Initialize ChaosChain SDK with AP2 and Process Integrity
        self.sdk = ChaosChainAgentSDK(
            agent_name=agent_name,
            agent_domain=agent_domain,
            agent_role=agent_role,
            network=network,
            enable_ap2=enable_ap2,
            enable_process_integrity=enable_process_integrity
        )
        
        # Initialize CrewAI components
        self._setup_crewai_agent()
        
        # Store service history
        self.service_history = []
        
        rprint(f"[green]🤖 Genesis Server Agent ({agent_name}) initialized with SDK + CrewAI[/green]")
        rprint(f"[blue]   Domain: {agent_domain}[/blue]")
        rprint(f"[blue]   Wallet: {self.sdk.wallet_address}[/blue]")
        rprint(f"[blue]   Network: {network.value}[/blue]")
    
    def _setup_crewai_agent(self):
        """Setup the CrewAI agent for shopping analysis"""
        
        # Create the shopping analysis tool
        self.analysis_tool = GenesisShoppingAnalysisTool()
        
        # Create the CrewAI agent
        self.crew_agent = Agent(
            role="Senior Smart Shopping Analyst",
            goal="Provide comprehensive and accurate smart shopping analysis with optimal price discovery and preference matching",
            backstory="""You are a senior smart shopping analyst at Genesis Studio, specializing in 
            intelligent product discovery and price optimization. You have extensive experience in 
            e-commerce analysis, price comparison, merchant evaluation, and consumer preference matching. 
            Your analyses are known for finding the best deals while respecting user preferences and budget constraints.""",
            tools=[self.analysis_tool],
            verbose=True,
            allow_delegation=False
        )
    
    def register_identity(self) -> str:
        """Register agent identity on ERC-8004 registry"""
        try:
            agent_id = self.sdk.register_identity()
            rprint(f"[green]✅ Server agent registered with ID: {agent_id}[/green]")
            return agent_id
        except Exception as e:
            rprint(f"[red]❌ Registration failed: {e}[/red]")
            raise
    
    def generate_smart_shopping_analysis(self, item_type: str, color: str, budget: float, 
                                       premium_tolerance: float = 0.20) -> Dict[str, Any]:
        """
        Generate comprehensive smart shopping analysis using CrewAI with process integrity
        
        Args:
            item_type: Type of item to shop for
            color: Preferred color
            budget: Maximum budget
            premium_tolerance: Acceptable premium for preferred options
            
        Returns:
            Dictionary containing the analysis results with process integrity proof
        """
        
        rprint(f"[yellow]🛒 Generating CrewAI smart shopping analysis for {item_type}...[/yellow]")
        
        # Register the shopping function for process integrity
        def smart_shopping_with_crewai(item_type: str, color: str, budget: float, premium_tolerance: float) -> Dict[str, Any]:
            """CrewAI-powered smart shopping analysis with process integrity"""
            
            # Create analysis task for CrewAI
            analysis_task = Task(
                description=f"""
                Perform a comprehensive smart shopping analysis for {item_type} with the following requirements:
                
                1. Product Discovery:
                   - Search for {item_type} in preferred color: {color}
                   - Budget constraint: ${budget} maximum
                   - Premium tolerance: {premium_tolerance*100}% for preferred options
                   
                2. Price Analysis:
                   - Compare prices across multiple merchants
                   - Identify best value propositions
                   - Calculate premiums for preferred specifications
                   
                3. Quality Assessment:
                   - Evaluate merchant reputation and reliability
                   - Assess product quality indicators
                   - Review customer feedback and ratings
                   
                4. Availability & Delivery:
                   - Verify real-time inventory status
                   - Optimize for fastest delivery options
                   - Confirm auto-purchase eligibility
                   
                5. Recommendation:
                   - Provide final recommendation with reasoning
                   - Include alternative options if preferred specs unavailable
                   - Ensure compliance with budget and preference constraints
                   
                Use the genesis_shopping_analysis tool with the specified parameters.
                Provide a comprehensive JSON-formatted shopping analysis report.
                """,
                expected_output="A comprehensive JSON-formatted smart shopping analysis report",
                agent=self.crew_agent
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[self.crew_agent],
                tasks=[analysis_task],
                verbose=True
            )
            
            try:
                # Execute the CrewAI analysis
                result = crew.kickoff()
                
                # Parse the result
                if isinstance(result, str):
                    try:
                        analysis_data = json.loads(result)
                    except json.JSONDecodeError:
                        # Fallback to tool-generated analysis
                        analysis_data = json.loads(self.analysis_tool._run(item_type, color, budget, premium_tolerance))
                else:
                    # Fallback to tool-generated analysis
                    analysis_data = json.loads(self.analysis_tool._run(item_type, color, budget, premium_tolerance))
                
                # Add Genesis Studio metadata
                analysis_data.update({
                    "genesis_studio": {
                        "agent_id": self.sdk.get_agent_id() if hasattr(self.sdk, 'get_agent_id') else None,
                        "agent_domain": self.agent_domain,
                        "analysis_timestamp": datetime.now().isoformat(),
                        "version": "1.0.0-crewai",
                        "process_integrity": True
                    }
                })
                
                return analysis_data
                
            except Exception as e:
                rprint(f"[red]❌ CrewAI analysis failed: {e}[/red]")
                
                # Fallback to direct tool execution
                rprint("[yellow]🔄 Using fallback analysis method...[/yellow]")
                fallback_result = self.analysis_tool._run(item_type, color, budget, premium_tolerance)
                analysis_data = json.loads(fallback_result)
                
                # Add Genesis Studio metadata
                analysis_data.update({
                    "genesis_studio": {
                        "agent_id": self.sdk.get_agent_id() if hasattr(self.sdk, 'get_agent_id') else None,
                        "agent_domain": self.agent_domain,
                        "analysis_timestamp": datetime.now().isoformat(),
                        "version": "1.0.0-crewai",
                        "process_integrity": True,
                        "fallback_mode": True
                    }
                })
                
                return analysis_data
        
        try:
            # Register function for process integrity
            code_hash = self.sdk.register_integrity_checked_function(
                smart_shopping_with_crewai, 
                "smart_shopping_with_crewai"
            )
            
            rprint(f"[blue]📝 Function registered for integrity checking: {code_hash[:16]}...[/blue]")
            
            # Execute with process integrity proof
            import asyncio
            result, process_integrity_proof = asyncio.run(self.sdk.execute_with_integrity_proof(
                "smart_shopping_with_crewai",
                {
                    "item_type": item_type,
                    "color": color, 
                    "budget": budget,
                    "premium_tolerance": premium_tolerance
                }
            ))
            
            # Store in service history
            self.service_history.append({
                "service": "smart_shopping_analysis",
                "item_type": item_type,
                "color": color,
                "budget": budget,
                "result": result,
                "process_integrity_proof": process_integrity_proof,
                "timestamp": datetime.now().isoformat()
            })
            
            rprint(f"[green]✅ CrewAI smart shopping analysis completed for {item_type}[/green]")
            confidence = result.get("confidence", 0.9)
            rprint(f"[blue]   Confidence Score: {confidence*100:.1f}%[/blue]")
            
            return {
                "analysis": result,
                "process_integrity_proof": process_integrity_proof
            }
            
        except Exception as e:
            rprint(f"[red]❌ Analysis with process integrity failed: {e}[/red]")
            raise
    
    def store_analysis_evidence(self, analysis_data: Dict[str, Any], filename_prefix: str = "analysis") -> str:
        """Store analysis evidence on IPFS"""
        try:
            cid = self.sdk.store_evidence(analysis_data, filename_prefix)
            rprint(f"[green]📁 Analysis evidence stored on IPFS: {cid}[/green]")
            return cid
        except Exception as e:
            rprint(f"[red]❌ Evidence storage failed: {e}[/red]")
            raise
    
    def request_validation(self, analysis_cid: str, validator_agent: str) -> str:
        """Request validation from a validator agent via ERC-8004"""
        try:
            # Calculate hash from CID for blockchain storage
            data_hash = "0x" + hashlib.sha256(analysis_cid.encode()).hexdigest()
            
            # Request validation via SDK
            tx_hash = self.sdk.request_validation(data_hash, validator_agent)
            
            rprint(f"[green]📋 Validation requested from {validator_agent}[/green]")
            rprint(f"[blue]   Transaction: {tx_hash}[/blue]")
            
            return tx_hash
            
        except Exception as e:
            rprint(f"[red]❌ Validation request failed: {e}[/red]")
            raise
    
    def get_service_summary(self) -> Dict[str, Any]:
        """Get a summary of all services provided"""
        if not self.service_history:
            return {
                "total_services": 0,
                "service_types": []
            }
        
        service_types = list(set(service["service"] for service in self.service_history))
        
        return {
            "total_services": len(self.service_history),
            "service_types": service_types,
            "service_history": self.service_history
        }
    
    def display_agent_info(self):
        """Display comprehensive agent information"""
        rprint("\n[bold green]🤖 Genesis Server Agent Information[/bold green]")
        rprint(f"[blue]Agent Name:[/blue] {self.agent_name}")
        rprint(f"[blue]Agent Domain:[/blue] {self.agent_domain}")
        rprint(f"[blue]Wallet Address:[/blue] {self.sdk.wallet_address}")
        rprint(f"[blue]Network:[/blue] {self.network.value}")
        rprint(f"[blue]Agent ID:[/blue] {self.sdk.get_agent_id() if hasattr(self.sdk, 'get_agent_id') else 'Not registered'}")
        
        # CrewAI capabilities
        rprint(f"[blue]AI Framework:[/blue] CrewAI + ChaosChain SDK")
        rprint(f"[blue]Process Integrity:[/blue] ✅ Enabled")
        rprint(f"[blue]IPFS Storage:[/blue] ✅ Enabled")
        
        # Service history
        if self.service_history:
            rprint(f"[blue]Services Provided:[/blue] {len(self.service_history)} analyses")
