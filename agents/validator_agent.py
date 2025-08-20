"""
Validator Agent - Market Analysis Validation Service

This agent demonstrates a Validator Agent role in the ERC-8004 ecosystem.
It uses CrewAI to validate market analysis work submitted by Server Agents
and provides validation scores through the ERC-8004 registries.
"""

import json
import os
from typing import Dict, Any, Optional
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from .base_agent import ERC8004BaseAgent

class ValidationInput(BaseModel):
    """Input model for validation analysis"""
    analysis_data: str = Field(description="The analysis data to validate")
    criteria: str = Field(description="Validation criteria to apply")

class ValidationTool(BaseTool):
    """Tool for performing validation analysis"""
    name: str = "validation_analysis"
    description: str = "Validates market analysis data against quality criteria"
    args_schema: type[BaseModel] = ValidationInput
    
    def _run(self, analysis_data: str, criteria: str) -> str:
        """
        Perform validation analysis
        """
        try:
            # Parse the analysis data
            data = json.loads(analysis_data) if isinstance(analysis_data, str) else analysis_data
            
            # Validation checks
            validation_results = {
                "completeness_score": 0,
                "accuracy_score": 0,
                "methodology_score": 0,
                "risk_assessment_score": 0,
                "issues_found": [],
                "strengths": []
            }
            
            # Check completeness
            required_fields = ["symbol", "analysis", "timestamp", "agent_id"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                validation_results["completeness_score"] = 100
                validation_results["strengths"].append("All required fields present")
            else:
                validation_results["completeness_score"] = max(0, 100 - len(missing_fields) * 25)
                validation_results["issues_found"].extend([f"Missing field: {field}" for field in missing_fields])
            
            # Check if analysis contains key components
            analysis_text = str(data.get("analysis", "")).lower()
            key_components = ["trend", "support", "resistance", "recommendation", "risk"]
            found_components = [comp for comp in key_components if comp in analysis_text]
            
            validation_results["methodology_score"] = (len(found_components) / len(key_components)) * 100
            
            if len(found_components) >= 4:
                validation_results["strengths"].append("Comprehensive analysis methodology")
            else:
                validation_results["issues_found"].append(f"Missing analysis components: {set(key_components) - set(found_components)}")
            
            # Check for risk assessment
            risk_indicators = ["risk", "warning", "caution", "volatility"]
            has_risk_assessment = any(indicator in analysis_text for indicator in risk_indicators)
            
            validation_results["risk_assessment_score"] = 100 if has_risk_assessment else 50
            
            if has_risk_assessment:
                validation_results["strengths"].append("Includes risk assessment")
            else:
                validation_results["issues_found"].append("Limited risk assessment")
            
            # Overall accuracy score (simplified)
            validation_results["accuracy_score"] = 85  # Would use more sophisticated checks in production
            
            return json.dumps(validation_results, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"Validation failed: {str(e)}",
                "completeness_score": 0,
                "accuracy_score": 0,
                "methodology_score": 0,
                "risk_assessment_score": 0
            })

class ValidatorAgent(ERC8004BaseAgent):
    """
    Validator Agent that validates market analysis work
    """
    
    def __init__(self, agent_domain: str, private_key: str):
        """Initialize the Validator Agent"""
        super().__init__(agent_domain, private_key)
        
        # Initialize CrewAI components
        self._setup_crew()
        
        print(f"🔍 Validator Agent initialized")
        print(f"   Domain: {self.agent_domain}")
        print(f"   Address: {self.address}")
    
    def _setup_crew(self):
        """Setup the CrewAI crew for validation"""
        
        # Create the validation tool
        self.validation_tool = ValidationTool()
        
        # Define the primary validator agent
        self.validator = Agent(
            role="Senior Analysis Validator",
            goal="Thoroughly validate market analysis reports for accuracy, completeness, and methodology",
            backstory="""You are an expert validator with deep knowledge of market analysis 
            methodologies. You have 15+ years of experience in financial analysis and 
            specialize in identifying flaws, inconsistencies, and areas for improvement 
            in market research reports.""",
            tools=[self.validation_tool],
            verbose=True,
            allow_delegation=False
        )
        
        # Define the quality assurance agent
        self.qa_specialist = Agent(
            role="Quality Assurance Specialist",
            goal="Ensure validation reports meet the highest standards and provide actionable feedback",
            backstory="""You are a quality assurance expert who specializes in reviewing 
            validation reports. Your role is to ensure that validation assessments are 
            fair, comprehensive, and provide constructive feedback for improvement.""",
            verbose=True,
            allow_delegation=False
        )
    
    def validate_analysis(self, data_hash: str) -> Dict[str, Any]:
        """
        Validate a market analysis using CrewAI
        
        Args:
            data_hash: Hash of the analysis data to validate
            
        Returns:
            Validation results with score
        """
        print(f"🔍 Starting validation for data hash: {data_hash}")
        
        # Load the analysis package
        analysis_package = self._load_analysis_package(data_hash)
        if not analysis_package:
            return {
                "error": "Analysis package not found",
                "score": 0,
                "validation_complete": False
            }
        
        # Create validation task
        validation_task = Task(
            description=f"""
            Validate the market analysis package with the following criteria:
            
            1. **Completeness**: Check if all required fields and components are present
            2. **Methodology**: Assess the analysis methodology and approach
            3. **Accuracy**: Evaluate the logical consistency of the analysis
            4. **Risk Assessment**: Verify appropriate risk warnings and disclaimers
            5. **Professional Standards**: Ensure the analysis meets industry standards
            
            Use the validation_analysis tool to perform systematic checks.
            Provide specific feedback on strengths and areas for improvement.
            
            Analysis to validate: {json.dumps(analysis_package, indent=2)}
            """,
            agent=self.validator,
            expected_output="A comprehensive validation report with scores for each criterion and specific feedback"
        )
        
        # Create quality assurance task
        qa_task = Task(
            description=f"""
            Review the validation assessment and provide:
            
            1. Verification of the validation methodology
            2. Assessment of the fairness and accuracy of scores
            3. Final validation score (0-100) based on all criteria
            4. Constructive feedback for the original analysis
            5. Recommendations for improvement
            
            Ensure the validation is thorough, fair, and provides actionable insights.
            """,
            agent=self.qa_specialist,
            expected_output="A final validation report with overall score and comprehensive feedback"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.validator, self.qa_specialist],
            tasks=[validation_task, qa_task],
            verbose=True
        )
        
        # Execute the validation
        try:
            result = crew.kickoff()
        except Exception as e:
            # Fallback to mock validation if LLM fails
            print(f"⚠️  LLM validation failed ({str(e)[:50]}...), using fallback validation")
            result = self._create_fallback_validation(analysis_package)
        
        # Extract validation score from the result
        validation_score = self._extract_validation_score(str(result))
        
        # Prepare the final validation package
        validation_package = {
            "data_hash": data_hash,
            "validator_agent_id": self.agent_id,
            "validator_domain": self.agent_domain,
            "timestamp": self.w3.eth.get_block('latest')['timestamp'],
            "validation_score": validation_score,
            "validation_report": str(result),
            "original_analysis": analysis_package,
            "metadata": {
                "validation_method": "CrewAI Multi-Agent Validation",
                "validator_agents": len(crew.agents),
                "validation_tasks": len(crew.tasks)
            }
        }
        
        print(f"✅ Validation completed with score: {validation_score}/100")
        return validation_package
    
    def submit_validation_response(self, validation_package: Dict[str, Any]) -> str:
        """
        Submit validation response through ERC-8004
        
        Args:
            validation_package: The completed validation
            
        Returns:
            Transaction hash of the validation response
        """
        data_hash = bytes.fromhex(validation_package["data_hash"])
        score = validation_package["validation_score"]
        
        print(f"📤 Submitting validation response")
        print(f"   Data hash: {validation_package['data_hash']}")
        print(f"   Score: {score}/100")
        
        # Store the validation package for reference
        self._store_validation_package(validation_package["data_hash"], validation_package)
        
        # Submit validation response through ERC-8004
        tx_hash = super().submit_validation_response(data_hash, score)
        
        return tx_hash
    
    def _load_analysis_package(self, data_hash: str) -> Optional[Dict[str, Any]]:
        """Load analysis package for validation (simplified for demo)"""
        try:
            with open(f"data/{data_hash}.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Analysis package not found: data/{data_hash}.json")
            return None
    
    def _store_validation_package(self, data_hash: str, validation_package: Dict[str, Any]):
        """Store validation package for reference (simplified for demo)"""
        os.makedirs("validations", exist_ok=True)
        
        with open(f"validations/{data_hash}.json", 'w') as f:
            json.dump(validation_package, f, indent=2)
        
        print(f"💾 Validation package stored: validations/{data_hash}.json")
    
    def _create_fallback_validation(self, analysis_package: Dict[str, Any]) -> str:
        """Create a fallback validation when LLM is not available"""
        # Simple validation logic
        required_fields = ["symbol", "analysis", "timestamp", "agent_id"]
        missing_fields = [field for field in required_fields if field not in analysis_package]
        
        completeness_score = 100 if not missing_fields else max(0, 100 - len(missing_fields) * 25)
        
        # Check if analysis contains key components
        analysis_text = str(analysis_package.get("analysis", "")).lower()
        key_components = ["trend", "support", "resistance", "recommendation", "risk"]
        found_components = [comp for comp in key_components if comp in analysis_text]
        methodology_score = (len(found_components) / len(key_components)) * 100
        
        # Overall score
        overall_score = int((completeness_score + methodology_score) / 2)
        
        return f"""
# Validation Report

## Analysis Quality Assessment

### Completeness Score: {completeness_score}/100
- Required fields present: {len(required_fields) - len(missing_fields)}/{len(required_fields)}
- Missing fields: {missing_fields if missing_fields else 'None'}

### Methodology Score: {methodology_score:.0f}/100
- Key components found: {len(found_components)}/{len(key_components)}
- Components: {', '.join(found_components)}

### Overall Validation Score: {overall_score}/100

## Summary
The analysis demonstrates {'good' if overall_score >= 80 else 'adequate' if overall_score >= 60 else 'basic'} quality with {'comprehensive' if len(found_components) >= 4 else 'partial'} coverage of required analytical components.

*Note: This validation was performed using fallback logic. For AI-powered validation with CrewAI, please configure your OpenAI API key.*
"""

    def _extract_validation_score(self, validation_result: str) -> int:
        """Extract numerical score from validation result"""
        # This is a simplified extraction - in production, you'd use more sophisticated parsing
        try:
            # Look for score patterns in the result
            import re
            
            # Try to find explicit score mentions
            score_patterns = [
                r'score[:\s]+(\d+)',
                r'(\d+)/100',
                r'(\d+)%',
                r'overall[:\s]+(\d+)'
            ]
            
            for pattern in score_patterns:
                matches = re.findall(pattern, validation_result.lower())
                if matches:
                    score = int(matches[-1])  # Take the last match
                    return min(100, max(0, score))  # Ensure 0-100 range
            
            # If no explicit score found, use heuristic based on content
            result_lower = validation_result.lower()
            
            if 'excellent' in result_lower or 'outstanding' in result_lower:
                return 95
            elif 'good' in result_lower or 'solid' in result_lower:
                return 85
            elif 'adequate' in result_lower or 'acceptable' in result_lower:
                return 75
            elif 'poor' in result_lower or 'inadequate' in result_lower:
                return 45
            else:
                return 70  # Default moderate score
                
        except Exception:
            return 70  # Default score if extraction fails
    
    def get_trust_models(self) -> list:
        """Return supported trust models for this agent"""
        return ["inference-validation", "crypto-economic"]
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Generate AgentCard following A2A specification"""
        return {
            "agentId": self.agent_id,
            "name": "Market Analysis Validator Agent",
            "description": "Validates cryptocurrency market analysis using AI-powered validation",
            "version": "1.0.0",
            "skills": [
                {
                    "skillId": "analysis-validation",
                    "name": "Analysis Validation",
                    "description": "Comprehensive validation of market analysis reports with scoring and feedback",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "data_hash": {"type": "string", "description": "Hash of analysis to validate"}
                        },
                        "required": ["data_hash"]
                    },
                    "outputSchema": {
                        "type": "object",
                        "properties": {
                            "validation_score": {"type": "number"},
                            "validation_report": {"type": "string"},
                            "feedback": {"type": "string"}
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