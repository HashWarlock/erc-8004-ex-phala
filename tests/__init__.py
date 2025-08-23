"""
ERC-8004 Trustless Agents Test Suite

This test suite provides comprehensive testing for the ERC-8004 Phala Cloud
implementation including unit tests, integration tests, and end-to-end tests.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)