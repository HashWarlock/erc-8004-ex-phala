#!/usr/bin/env python3
"""
Custom Validation Example

Demonstrates specialized validation logic with domain-specific rules,
multi-factor validation, and consensus mechanisms.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import hashlib
from typing import Dict, List, Any, Optional
from enum import Enum

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from src.agent.base import AgentConfig, AgentRole, RegistryAddresses
from src.templates.validator_agent import ValidatorAgent


class ValidationLevel(Enum):
    """Validation strictness levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CustomValidatorAgent(ValidatorAgent):
    """Validator with custom domain-specific validation logic."""

    def __init__(self, config, registries):
        super().__init__(config, registries)
        self.setup_custom_validators()

    def setup_custom_validators(self):
        """Initialize custom validation plugins."""
        # Add domain-specific validators
        self.add_plugin('financial_validator', FinancialDataValidator())
        self.add_plugin('security_validator', SecurityValidator())
        self.add_plugin('compliance_validator', ComplianceValidator())
        self.add_plugin('consensus_validator', ConsensusValidator())

    async def validate_with_custom_rules(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom validation rules based on data type."""
        validation_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'validators_applied': [],
            'issues': [],
            'recommendations': [],
            'overall_valid': True,
            'confidence': 1.0
        }

        # Determine which validators to apply
        data_type = data.get('type', 'generic')
        validation_level = ValidationLevel(data.get('validation_level', 'medium'))

        # Financial validation
        if data_type in ['financial', 'transaction', 'payment']:
            financial_result = await self.get_plugin('financial_validator').validate(
                data, validation_level
            )
            validation_results['validators_applied'].append('financial')
            validation_results['financial'] = financial_result
            if not financial_result['valid']:
                validation_results['overall_valid'] = False
                validation_results['issues'].extend(financial_result.get('issues', []))

        # Security validation
        if validation_level in [ValidationLevel.HIGH, ValidationLevel.CRITICAL]:
            security_result = await self.get_plugin('security_validator').validate(
                data, validation_level
            )
            validation_results['validators_applied'].append('security')
            validation_results['security'] = security_result
            if not security_result['valid']:
                validation_results['overall_valid'] = False
                validation_results['issues'].extend(security_result.get('issues', []))

        # Compliance validation
        if data.get('requires_compliance', False):
            compliance_result = await self.get_plugin('compliance_validator').validate(
                data, validation_level
            )
            validation_results['validators_applied'].append('compliance')
            validation_results['compliance'] = compliance_result
            if not compliance_result['valid']:
                validation_results['overall_valid'] = False
                validation_results['issues'].extend(compliance_result.get('issues', []))

        # Consensus validation for critical operations
        if validation_level == ValidationLevel.CRITICAL:
            consensus_result = await self.get_plugin('consensus_validator').validate(
                data, validation_results
            )
            validation_results['validators_applied'].append('consensus')
            validation_results['consensus'] = consensus_result
            validation_results['confidence'] = consensus_result.get('consensus_score', 0.5)

        return validation_results


class FinancialDataValidator:
    """Validates financial data and transactions."""

    async def validate(self, data: Dict[str, Any], level: ValidationLevel) -> Dict[str, Any]:
        """Perform financial validation checks."""
        result = {
            'valid': True,
            'issues': [],
            'checks_performed': [],
            'metrics': {}
        }

        # Amount validation
        if 'amount' in data:
            amount = data['amount']
            result['checks_performed'].append('amount_validation')

            if amount < 0:
                result['valid'] = False
                result['issues'].append('Negative amount detected')

            if level == ValidationLevel.CRITICAL and amount > 1000000:
                result['valid'] = False
                result['issues'].append('Amount exceeds critical threshold')

            result['metrics']['amount'] = amount

        # Currency validation
        if 'currency' in data:
            result['checks_performed'].append('currency_validation')
            valid_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'ETH', 'BTC']

            if data['currency'] not in valid_currencies:
                result['valid'] = False
                result['issues'].append(f"Invalid currency: {data['currency']}")

        # Transaction rate limiting
        if 'transaction_count' in data:
            result['checks_performed'].append('rate_limiting')
            tx_count = data['transaction_count']

            if level == ValidationLevel.HIGH and tx_count > 100:
                result['issues'].append('High transaction rate detected')

            if tx_count > 1000:
                result['valid'] = False
                result['issues'].append('Transaction rate limit exceeded')

        # Price deviation checks
        if 'price' in data and 'expected_price' in data:
            result['checks_performed'].append('price_deviation')
            deviation = abs(data['price'] - data['expected_price']) / data['expected_price']

            if deviation > 0.1:  # 10% deviation
                result['issues'].append(f'Price deviation: {deviation:.2%}')

            if deviation > 0.25:  # 25% deviation
                result['valid'] = False
                result['issues'].append('Critical price deviation detected')

        await asyncio.sleep(0.1)  # Simulate processing time
        return result


class SecurityValidator:
    """Validates security aspects of data."""

    async def validate(self, data: Dict[str, Any], level: ValidationLevel) -> Dict[str, Any]:
        """Perform security validation checks."""
        result = {
            'valid': True,
            'issues': [],
            'security_score': 100,
            'checks_performed': []
        }

        # Signature validation
        if 'signature' in data:
            result['checks_performed'].append('signature_validation')
            is_valid_sig = await self._verify_signature(data)

            if not is_valid_sig:
                result['valid'] = False
                result['issues'].append('Invalid signature')
                result['security_score'] -= 50

        # Data integrity check
        if 'data_hash' in data and 'raw_data' in data:
            result['checks_performed'].append('integrity_check')
            computed_hash = hashlib.sha256(
                json.dumps(data['raw_data'], sort_keys=True).encode()
            ).hexdigest()

            if computed_hash != data['data_hash']:
                result['valid'] = False
                result['issues'].append('Data integrity check failed')
                result['security_score'] -= 30

        # Timestamp validation
        if 'timestamp' in data:
            result['checks_performed'].append('timestamp_validation')
            try:
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                time_diff = abs((datetime.utcnow() - timestamp.replace(tzinfo=None)).total_seconds())

                if time_diff > 300:  # 5 minutes
                    result['issues'].append('Timestamp outside acceptable range')
                    result['security_score'] -= 10

                if time_diff > 3600:  # 1 hour
                    result['valid'] = False
                    result['issues'].append('Timestamp too old')
                    result['security_score'] -= 20

            except Exception as e:
                result['valid'] = False
                result['issues'].append(f'Invalid timestamp format: {e}')
                result['security_score'] -= 25

        # Source validation
        if 'source' in data:
            result['checks_performed'].append('source_validation')
            trusted_sources = ['verified_agent', 'tee_environment', 'blockchain']

            if data['source'] not in trusted_sources:
                result['issues'].append(f"Untrusted source: {data['source']}")
                result['security_score'] -= 15

        # Anomaly detection
        if level == ValidationLevel.CRITICAL:
            result['checks_performed'].append('anomaly_detection')
            anomalies = await self._detect_anomalies(data)

            if anomalies:
                result['issues'].extend(anomalies)
                result['security_score'] -= len(anomalies) * 5

        result['security_score'] = max(0, result['security_score'])
        if result['security_score'] < 50:
            result['valid'] = False

        await asyncio.sleep(0.1)  # Simulate processing time
        return result

    async def _verify_signature(self, data: Dict[str, Any]) -> bool:
        """Verify cryptographic signature."""
        # Simplified signature verification
        return len(data.get('signature', '')) == 132  # Hex signature length

    async def _detect_anomalies(self, data: Dict[str, Any]) -> List[str]:
        """Detect anomalies in data patterns."""
        anomalies = []

        # Check for suspicious patterns
        if 'request_count' in data and data['request_count'] > 1000:
            anomalies.append('Abnormal request volume')

        if 'user_agent' in data and 'bot' in data['user_agent'].lower():
            anomalies.append('Bot activity detected')

        return anomalies


class ComplianceValidator:
    """Validates compliance with regulations and policies."""

    async def validate(self, data: Dict[str, Any], level: ValidationLevel) -> Dict[str, Any]:
        """Perform compliance validation checks."""
        result = {
            'valid': True,
            'issues': [],
            'regulations_checked': [],
            'compliance_score': 100
        }

        # GDPR compliance
        if data.get('region') == 'EU' or data.get('check_gdpr', False):
            result['regulations_checked'].append('GDPR')
            gdpr_result = await self._check_gdpr_compliance(data)

            if not gdpr_result['compliant']:
                result['issues'].extend(gdpr_result['violations'])
                result['compliance_score'] -= 20 * len(gdpr_result['violations'])

        # KYC/AML checks
        if data.get('financial_operation', False):
            result['regulations_checked'].append('KYC/AML')
            kyc_result = await self._check_kyc_aml(data)

            if not kyc_result['compliant']:
                result['valid'] = False
                result['issues'].extend(kyc_result['violations'])
                result['compliance_score'] -= 30

        # Data retention policies
        if 'data_retention' in data:
            result['regulations_checked'].append('Data Retention')
            retention_days = data['data_retention']

            if retention_days > 365:
                result['issues'].append('Data retention exceeds policy limit')
                result['compliance_score'] -= 10

            if retention_days < 30:
                result['issues'].append('Data retention below minimum requirement')
                result['compliance_score'] -= 10

        # License compliance
        if 'licenses' in data:
            result['regulations_checked'].append('License Compliance')
            for license_type in data['licenses']:
                if license_type not in ['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3']:
                    result['issues'].append(f'Non-compliant license: {license_type}')
                    result['compliance_score'] -= 15

        result['compliance_score'] = max(0, result['compliance_score'])
        if result['compliance_score'] < 50:
            result['valid'] = False

        await asyncio.sleep(0.1)  # Simulate processing time
        return result

    async def _check_gdpr_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check GDPR compliance."""
        violations = []

        if data.get('personal_data', False) and not data.get('consent', False):
            violations.append('Personal data processing without consent')

        if not data.get('data_protection_officer', False):
            violations.append('No data protection officer assigned')

        return {'compliant': len(violations) == 0, 'violations': violations}

    async def _check_kyc_aml(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check KYC/AML compliance."""
        violations = []

        if not data.get('identity_verified', False):
            violations.append('Identity not verified')

        if data.get('amount', 0) > 10000 and not data.get('source_of_funds', False):
            violations.append('Large transaction without source of funds verification')

        return {'compliant': len(violations) == 0, 'violations': violations}


class ConsensusValidator:
    """Aggregates multiple validation results for consensus."""

    async def validate(self, data: Dict[str, Any], validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build consensus from multiple validators."""
        result = {
            'valid': True,
            'consensus_score': 0.0,
            'validators_agree': False,
            'dissenting_validators': []
        }

        # Collect all validator results
        validator_scores = {}
        for validator_name in validation_results.get('validators_applied', []):
            if validator_name in validation_results:
                validator_result = validation_results[validator_name]
                validator_scores[validator_name] = 1.0 if validator_result.get('valid', False) else 0.0

        # Calculate consensus
        if validator_scores:
            total_score = sum(validator_scores.values())
            num_validators = len(validator_scores)
            result['consensus_score'] = total_score / num_validators

            # Check for agreement
            if total_score == num_validators or total_score == 0:
                result['validators_agree'] = True
            else:
                # Find dissenting validators
                for name, score in validator_scores.items():
                    if (score == 0 and result['consensus_score'] > 0.5) or \
                       (score == 1 and result['consensus_score'] < 0.5):
                        result['dissenting_validators'].append(name)

            # Determine overall validity based on consensus threshold
            result['valid'] = result['consensus_score'] >= 0.66  # 2/3 majority

        await asyncio.sleep(0.05)  # Simulate processing time
        return result


class CustomValidationDemo:
    """Orchestrates custom validation demonstration."""

    def __init__(self):
        """Initialize the demo."""
        load_dotenv()
        self.validator = None

    async def setup_validator(self):
        """Initialize custom validator agent."""
        print("🚀 Setting up Custom Validation Demo")
        print("=" * 50)

        registries = RegistryAddresses(
            identity=os.getenv('IDENTITY_REGISTRY_ADDRESS', '0x000c5A70B7269c5eD4238DcC6576e598614d3f70'),
            reputation=os.getenv('REPUTATION_REGISTRY_ADDRESS', '0xa7b860b16a41Aa8b6990EB3Fec0dB34686f7EAde'),
            validation=os.getenv('VALIDATION_REGISTRY_ADDRESS', '0xA455e56CBE75aaa3F692d28d0fBFD1D44B64F70d'),
            tee_verifier=os.getenv('TEE_VERIFIER_ADDRESS', '0x1b841e88ba786027f39ecf9Cd160176b22E3603c')
        )

        use_tee = os.getenv('USE_TEE_AUTH', 'false').lower() == 'true'
        rpc_url = os.getenv('RPC_URL', 'https://sepolia.base.org')
        chain_id = int(os.getenv('CHAIN_ID', '84532'))

        print("\n🔍 Initializing Custom Validator Agent...")
        validator_config = AgentConfig(
            domain="custom-validator.example.com",
            salt="custom-validator-salt",
            role=AgentRole.VALIDATOR,
            rpc_url=rpc_url,
            chain_id=chain_id,
            use_tee_auth=use_tee,
            private_key=os.getenv('VALIDATOR_PRIVATE_KEY') if not use_tee else None
        )
        self.validator = CustomValidatorAgent(validator_config, registries)
        print("✅ Custom Validator initialized!")

    async def demonstrate_validation_scenarios(self):
        """Run various validation scenarios."""
        print("\n" + "=" * 50)
        print("🎭 Custom Validation Scenarios")
        print("=" * 50)

        # Scenario 1: Financial Transaction Validation
        print("\n📊 Scenario 1: Financial Transaction Validation")
        financial_data = {
            'type': 'financial',
            'validation_level': 'high',
            'amount': 50000,
            'currency': 'USD',
            'transaction_count': 50,
            'price': 105,
            'expected_price': 100,
            'timestamp': datetime.utcnow().isoformat(),
            'signature': '0x' + 'a' * 130,  # Mock signature
            'data_hash': hashlib.sha256(b'test_data').hexdigest()
        }

        result1 = await self.validator.validate_with_custom_rules(financial_data)
        self._print_validation_result("Financial", result1)

        # Scenario 2: Critical Security Validation
        print("\n🔐 Scenario 2: Critical Security Validation")
        security_data = {
            'type': 'authentication',
            'validation_level': 'critical',
            'timestamp': (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
            'signature': '0x' + 'b' * 130,
            'source': 'tee_environment',
            'raw_data': {'user': 'alice', 'action': 'login'},
            'data_hash': hashlib.sha256(
                json.dumps({'user': 'alice', 'action': 'login'}, sort_keys=True).encode()
            ).hexdigest(),
            'request_count': 100
        }

        result2 = await self.validator.validate_with_custom_rules(security_data)
        self._print_validation_result("Security", result2)

        # Scenario 3: Compliance-Required Operation
        print("\n📋 Scenario 3: Compliance-Required Operation")
        compliance_data = {
            'type': 'data_processing',
            'validation_level': 'high',
            'requires_compliance': True,
            'region': 'EU',
            'personal_data': True,
            'consent': True,
            'data_protection_officer': True,
            'financial_operation': True,
            'identity_verified': True,
            'amount': 5000,
            'source_of_funds': True,
            'data_retention': 90,
            'licenses': ['MIT', 'Apache-2.0']
        }

        result3 = await self.validator.validate_with_custom_rules(compliance_data)
        self._print_validation_result("Compliance", result3)

        # Scenario 4: Failed Validation
        print("\n❌ Scenario 4: Failed Validation Example")
        invalid_data = {
            'type': 'financial',
            'validation_level': 'critical',
            'amount': -1000,  # Invalid negative amount
            'currency': 'INVALID',  # Invalid currency
            'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),  # Old timestamp
            'signature': 'invalid',  # Invalid signature
            'requires_compliance': True,
            'personal_data': True,
            'consent': False  # No consent
        }

        result4 = await self.validator.validate_with_custom_rules(invalid_data)
        self._print_validation_result("Invalid", result4)

        # Summary
        print("\n" + "=" * 50)
        print("📊 Validation Summary")
        print("=" * 50)

        summary = {
            'scenarios_tested': 4,
            'validators_available': ['financial', 'security', 'compliance', 'consensus'],
            'results': {
                'financial': result1['overall_valid'],
                'security': result2['overall_valid'],
                'compliance': result3['overall_valid'],
                'invalid': result4['overall_valid']
            },
            'features_demonstrated': [
                'Multi-factor validation',
                'Domain-specific rules',
                'Compliance checking',
                'Security validation',
                'Consensus building'
            ]
        }

        print(json.dumps(summary, indent=2))
        return summary

    def _print_validation_result(self, scenario: str, result: Dict[str, Any]):
        """Pretty print validation results."""
        status = "✅ VALID" if result['overall_valid'] else "❌ INVALID"
        print(f"  Status: {status}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Validators Applied: {', '.join(result['validators_applied'])}")

        if result['issues']:
            print(f"  Issues Found:")
            for issue in result['issues'][:3]:  # Show first 3 issues
                print(f"    - {issue}")

        if result.get('consensus'):
            consensus = result['consensus']
            print(f"  Consensus Score: {consensus['consensus_score']:.2f}")
            if consensus['dissenting_validators']:
                print(f"  Dissenting: {', '.join(consensus['dissenting_validators'])}")


async def main():
    """Run the custom validation demonstration."""
    demo = CustomValidationDemo()

    try:
        await demo.setup_validator()
        result = await demo.demonstrate_validation_scenarios()
        print("\n✨ Custom validation demonstration completed successfully!")

    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║  ERC-8004 TEE Agents - Custom Validation║
    ║                                          ║
    ║  Domain-Specific Validation Rules       ║
    ╚══════════════════════════════════════════╝
    """)

    asyncio.run(main())