"""
TEE-Enabled Validator Agent - Validation Service

This agent demonstrates a TEE-enabled Validator Agent role in the ERC-8004 ecosystem.
It uses CrewAI to validate analysis work from other agents and submits validation
responses through the ERC-8004 registries, with keys derived from the TEE.
"""

import json
import os
from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from .tee_base_agent import ERC8004TEEAgent


class ValidationInput(BaseModel):
    """Input model for validation"""

    data_hash: str = Field(description="Hash of the data to validate")


class ValidationTool(BaseTool):
    """Tool for validating analysis data"""

    name: str = "validate_analysis"
    description: str = "Validates analysis data against quality criteria"
    args_schema: type[BaseModel] = ValidationInput

    def _run(self, data_hash: str) -> str:
        """
        Validate analysis data (simplified for demo)
        In a real implementation, this would fetch and analyze the actual data
        """
        # Load the analysis package
        try:
            with open(f"data/{data_hash}.json", "r") as f:
                analysis = json.load(f)

            # Perform validation checks
            validation_result = {
                "data_hash": data_hash,
                "completeness_score": 100
                if all(k in analysis for k in ["symbol", "timeframe", "analysis"])
                else 50,
                "accuracy_score": 85,  # Simulated accuracy check
                "methodology_score": 90,  # Simulated methodology assessment
                "issues_found": [],
                "recommendations": [
                    "Consider adding more technical indicators",
                    "Include volume analysis for better confirmation",
                ],
            }

            return json.dumps(validation_result, indent=2)
        except FileNotFoundError:
            return json.dumps(
                {"error": "Analysis data not found", "data_hash": data_hash}
            )


class TEEValidatorAgent(ERC8004TEEAgent):
    """
    TEE-enabled Validator Agent that validates work from other agents
    """

    def __init__(
        self, agent_domain: str, salt: str, tee_endpoint: Optional[str] = None
    ):
        """Initialize the TEE Validator Agent"""
        super().__init__(agent_domain, salt, tee_endpoint)

        # Initialize CrewAI components
        self._setup_crew()

        print(f"🔍 TEE Validator Agent initialized")
        print(f"   Domain: {self.agent_domain}")
        print(f"   Address: {self.address}")
        print(f"   TEE: Enabled ✅")

    def _setup_crew(self):
        """Setup the CrewAI crew for validation"""

        # Create the validation tool
        self.validation_tool = ValidationTool()

        # Define the validator agent
        self.validator = Agent(
            role="Senior Validation Specialist",
            goal="Thoroughly validate and assess the quality of market analysis reports",
            backstory="""You are an expert validator with extensive experience in 
            assessing the quality and accuracy of financial analysis. You ensure that 
            all analyses meet professional standards and provide valuable insights.""",
            tools=[self.validation_tool],
            verbose=True,
            allow_delegation=False,
        )

        # Define the quality assurance agent
        self.qa_agent = Agent(
            role="Quality Assurance Expert",
            goal="Review validation results and ensure comprehensive assessment",
            backstory="""You specialize in quality assurance for financial reports. 
            Your role is to ensure that validations are thorough, fair, and provide 
            constructive feedback for improvement.""",
            verbose=True,
            allow_delegation=False,
        )

    def validate_analysis(self, data_hash: str) -> Dict[str, Any]:
        """
        Validate analysis work using CrewAI

        Args:
            data_hash: Hash of the analysis data to validate

        Returns:
            Validation results with score and feedback
        """
        # Handle both hash string and actual analysis data
        if isinstance(data_hash, dict):
            # If we received the actual analysis data
            original_analysis = data_hash
            import hashlib
            data_str = json.dumps(original_analysis, sort_keys=True)
            computed_hash = hashlib.sha256(data_str.encode()).hexdigest()
            print(f"🔍 Starting validation for analysis data (hash: {computed_hash[:16]}...)")
            actual_hash = computed_hash
        else:
            # If we received a hash string
            print(f"🔍 Starting validation for data hash: {data_hash[:16]}...")
            actual_hash = data_hash
            # Load the original analysis
            try:
                with open(f"data/{data_hash}.json", "r") as f:
                    original_analysis = json.load(f)
            except FileNotFoundError:
                print(f"❌ Analysis data not found: {data_hash}")
                return {"error": "Analysis data not found", "data_hash": data_hash}

        # Get hash string for display
        hash_str = computed_hash if isinstance(data_hash, dict) else str(data_hash)
        
        # Create validation task
        validation_task = Task(
            description=f"""
            Validate the market analysis with hash {hash_str[:16]}... by:
            
            1. Verifying the completeness of the analysis
            2. Assessing the accuracy and logic of conclusions
            3. Evaluating the methodology used
            4. Identifying any potential issues or gaps
            5. Providing a validation score (0-100)
            
            Use the validate_analysis tool to examine the data.
            Provide a comprehensive validation report.
            """,
            agent=self.validator,
            expected_output="A detailed validation report with scores, findings, and recommendations",
        )

        # Create QA review task
        qa_task = Task(
            description=f"""
            Review the validation report and ensure:
            
            1. The validation methodology is sound
            2. Scores are fair and justified
            3. Feedback is constructive and actionable
            4. All critical aspects have been assessed
            
            Provide a final validation score and summary.
            """,
            agent=self.qa_agent,
            expected_output="A final validation assessment with confirmed score and feedback",
        )

        # Create and run the crew
        crew = Crew(
            agents=[self.validator, self.qa_agent],
            tasks=[validation_task, qa_task],
            verbose=True,
        )

        # Execute the validation
        try:
            result = crew.kickoff()
        except Exception as e:
            # Fallback to mock validation if LLM fails
            print(
                f"⚠️  LLM validation failed ({str(e)[:50]}...), using fallback validation"
            )
            result = self._create_fallback_validation(actual_hash, original_analysis)

        # Calculate final score (simplified - in production would parse from result)
        validation_score = self._calculate_validation_score(str(result))

        # Include TEE attestation in the validation package
        attestation = self.get_attestation()

        # Prepare validation package
        validation_package = {
            "data_hash": actual_hash,
            "validator_agent_id": self.agent_id,
            "validator_domain": self.agent_domain,
            "timestamp": self.w3.eth.get_block("latest")["timestamp"],
            "validation_score": validation_score,
            "validation_report": str(result),
            "original_analysis": original_analysis,
            "metadata": {
                "validation_method": "CrewAI Multi-Agent Validation",
                "validator_agents": len(crew.agents),
                "validation_tasks": len(crew.tasks),
                "tee_enabled": True,
                "tee_validated": True,
                "attestation_available": attestation is not None,
                "attestation": attestation,
            },
        }

        # Store validation package
        self._store_validation_package(actual_hash, validation_package)

        print(f"✅ Validation completed with score: {validation_score}/100")
        
        # Return in the expected format for tests
        return {
            "is_valid": validation_score >= 70,
            "score": validation_score,
            "validation_package": validation_package,
            "report": str(result),
            "metadata": validation_package["metadata"]  # For backward compatibility
        }

    def submit_validation(self, validation_package: Dict[str, Any]) -> str:
        """
        Submit validation response to the blockchain

        Args:
            validation_package: The completed validation package

        Returns:
            Transaction hash
        """
        data_hash = bytes.fromhex(validation_package["data_hash"])
        score = validation_package["validation_score"]

        print(f"📤 Submitting validation response: {score}/100")

        # Submit to blockchain (using parent class method)
        tx_hash = self.submit_validation_response(data_hash, score)

        print(f"✅ Validation response submitted: {tx_hash}")
        return tx_hash

    def _calculate_validation_score(self, result: str) -> int:
        """
        Calculate validation score from the result
        In production, this would parse the actual score from the LLM output
        """
        # Simple heuristic for demo
        if "high quality" in result.lower() or "excellent" in result.lower():
            return 95
        elif "good" in result.lower() or "satisfactory" in result.lower():
            return 85
        elif "adequate" in result.lower() or "acceptable" in result.lower():
            return 75
        else:
            return 65

    def _create_fallback_validation(
        self, data_hash: str, original_analysis: Dict[str, Any]
    ) -> str:
        """Create fallback validation when LLM is not available"""
        # Basic validation logic
        score = 85
        issues = []

        if "symbol" not in original_analysis:
            score -= 10
            issues.append("Missing symbol information")

        if "analysis" not in original_analysis:
            score -= 20
            issues.append("Missing analysis content")

        return f"""
# Validation Report

## Data Hash
{data_hash[:16]}...

## Validation Summary
The analysis has been reviewed and validated with a score of **{score}/100**.

## Assessment Criteria

### 1. Completeness
The analysis includes all required fields and comprehensive market assessment.
Score: {100 if not issues else 80}/100

### 2. Methodology
The analytical approach appears sound and follows standard practices.
Score: 85/100

### 3. Accuracy
Based on available data, the conclusions are reasonable and well-supported.
Score: {score}/100

## Issues Found
{chr(10).join(f"- {issue}" for issue in issues) if issues else "No critical issues identified."}

## Recommendations
- Continue monitoring market conditions for validation
- Consider adding more technical indicators for enhanced accuracy
- Include risk management strategies in future analyses

## Final Score
**{score}/100** - The analysis meets professional standards with room for minor improvements.

*Note: This validation was generated using fallback logic. For AI-powered validation with CrewAI, please configure your OpenAI API key.*
"""

    def _store_validation_package(
        self, data_hash: str, validation_package: Dict[str, Any]
    ):
        """Store validation package (simplified for demo)"""
        os.makedirs("validations", exist_ok=True)

        with open(f"validations/{data_hash}.json", "w") as f:
            json.dump(validation_package, f, indent=2)

        print(f"💾 Validation package stored: validations/{data_hash}.json")

    def get_trust_models(self) -> list:
        """Return supported trust models for this agent"""
        return ["inference-validation", "cryptoeconomic-validation", "tee-attestation"]

    def get_agent_card(self) -> Dict[str, Any]:
        """Generate AgentCard following A2A specification"""
        return {
            "agentId": self.agent_id,
            "name": "TEE-Enabled Validation Agent",
            "description": "Provides thorough validation of analysis work with TEE security",
            "version": "1.0.0",
            "skills": [
                {
                    "skillId": "validate-analysis",
                    "name": "Analysis Validation",
                    "description": "Comprehensive validation of market analysis reports",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "data_hash": {
                                "type": "string",
                                "description": "Hash of data to validate",
                            }
                        },
                        "required": ["data_hash"],
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "validation_score": {"type": "number"},
                            "validation_report": {"type": "string"},
                            "metadata": {"type": "object"},
                        },
                    },
                }
            ],
            "trustModels": self.get_trust_models(),
            "registrations": [
                {
                    "agentId": self.agent_id,
                    "agentAddress": f"eip155:{self.w3.eth.chain_id}:{self.address}",
                    "signature": "0x...",  # Would be actual signature in production
                    "teeAttestation": self.get_attestation(),
                }
            ],
        }
