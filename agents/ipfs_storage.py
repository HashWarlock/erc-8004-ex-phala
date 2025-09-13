"""
Genesis Studio - IPFS Storage Module

This module handles storing analysis reports and validation data on IPFS using Pinata.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from rich.console import Console
from rich import print as rprint

console = Console()

class PinataIPFSStorage:
    """Handles IPFS storage operations via Pinata API"""
    
    def __init__(self):
        self.jwt_token = os.getenv("PINATA_JWT")
        self.gateway_url = os.getenv("PINATA_GATEWAY")
        
        if not self.jwt_token:
            raise ValueError("PINATA_JWT environment variable is required")
        if not self.gateway_url:
            raise ValueError("PINATA_GATEWAY environment variable is required")
        
        self.base_url = "https://api.pinata.cloud"
        self.headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
    
    def upload_json(self, data: Dict[Any, Any], filename: str) -> Optional[str]:
        """Upload JSON data to IPFS and return the CID"""
        
        try:
            # Convert data to JSON string
            json_content = json.dumps(data, indent=2)
            
            # Prepare the file for upload
            files = {
                'file': (filename, json_content, 'application/json')
            }
            
            # Remove Content-Type header for file upload
            upload_headers = {
                "Authorization": f"Bearer {self.jwt_token}"
            }
            
            with console.status(f"[bold blue]Uploading {filename} to IPFS..."):
                response = requests.post(
                    f"{self.base_url}/pinning/pinFileToIPFS",
                    files=files,
                    headers=upload_headers
                )
            
            if response.status_code == 200:
                result = response.json()
                cid = result.get("IpfsHash")
                
                rprint(f"[green]📁 Successfully uploaded {filename} to IPFS")
                rprint(f"[blue]   CID: {cid}")
                rprint(f"[blue]   Gateway URL: https://{self.gateway_url}/ipfs/{cid}")
                
                return cid
            else:
                rprint(f"[red]❌ Failed to upload {filename}: {response.text}")
                return None
                
        except Exception as e:
            rprint(f"[red]❌ Error uploading {filename}: {e}")
            return None
    
    def retrieve_json(self, cid: str) -> Optional[Dict[Any, Any]]:
        """Retrieve JSON data from IPFS using CID"""
        
        try:
            gateway_url = f"https://{self.gateway_url}/ipfs/{cid}"
            
            with console.status(f"[bold blue]Retrieving data from IPFS..."):
                response = requests.get(gateway_url)
            
            if response.status_code == 200:
                data = response.json()
                rprint(f"[green]📥 Successfully retrieved data from IPFS")
                rprint(f"[blue]   CID: {cid}")
                return data
            else:
                rprint(f"[red]❌ Failed to retrieve data: {response.status_code}")
                return None
                
        except Exception as e:
            rprint(f"[red]❌ Error retrieving data: {e}")
            return None
    
    def get_gateway_url(self, cid: str) -> str:
        """Get the full gateway URL for a CID"""
        return f"https://{self.gateway_url}/ipfs/{cid}"
    
    def pin_status(self, cid: str) -> Optional[Dict[str, Any]]:
        """Check the pin status of a CID"""
        
        try:
            response = requests.get(
                f"{self.base_url}/data/pinList?hashContains={cid}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                rprint(f"[red]❌ Failed to check pin status: {response.text}")
                return None
                
        except Exception as e:
            rprint(f"[red]❌ Error checking pin status: {e}")
            return None

class GenesisIPFSManager:
    """High-level IPFS manager for Genesis Studio operations"""
    
    def __init__(self):
        self.storage = PinataIPFSStorage()
    
    def store_analysis_report(self, analysis_data: Dict[str, Any], agent_id: int) -> Optional[str]:
        """Store market analysis report on IPFS"""
        
        # Add metadata
        report = {
            "type": "market_analysis",
            "agent_id": agent_id,
            "timestamp": analysis_data.get("timestamp"),
            "analysis": analysis_data,
            "genesis_studio_version": "1.0.0"
        }
        
        filename = f"analysis_agent_{agent_id}_{analysis_data.get('timestamp', 'unknown')}.json"
        return self.storage.upload_json(report, filename)
    
    def store_validation_report(self, validation_data: Dict[str, Any], validator_id: int, data_hash: str) -> Optional[str]:
        """Store validation report on IPFS"""
        
        # Add metadata
        report = {
            "type": "validation_report",
            "validator_id": validator_id,
            "data_hash": data_hash,
            "timestamp": validation_data.get("timestamp"),
            "validation": validation_data,
            "genesis_studio_version": "1.0.0"
        }
        
        filename = f"validation_agent_{validator_id}_{data_hash[:8]}.json"
        return self.storage.upload_json(report, filename)
    
    def retrieve_analysis_report(self, cid: str) -> Optional[Dict[str, Any]]:
        """Retrieve and validate analysis report from IPFS"""
        
        data = self.storage.retrieve_json(cid)
        if data and data.get("type") == "market_analysis":
            return data
        return None
    
    def retrieve_validation_report(self, cid: str) -> Optional[Dict[str, Any]]:
        """Retrieve and validate validation report from IPFS"""
        
        data = self.storage.retrieve_json(cid)
        if data and data.get("type") == "validation_report":
            return data
        return None
    
    def store_generic_evidence(self, evidence_data: Dict[str, Any], agent_id: int, evidence_type: str) -> Optional[str]:
        """Store generic evidence on IPFS"""
        
        # Add metadata
        report = {
            "type": f"evidence_{evidence_type}",
            "agent_id": agent_id,
            "evidence_type": evidence_type,
            "timestamp": evidence_data.get("timestamp"),
            "evidence": evidence_data,
            "genesis_studio_version": "1.0.0"
        }
        
        filename = f"evidence_{evidence_type}_agent_{agent_id}_{evidence_data.get('timestamp', 'unknown')}.json"
        return self.storage.upload_json(report, filename)
    
    def retrieve_generic_evidence(self, cid: str) -> Optional[Dict[str, Any]]:
        """Retrieve generic evidence from IPFS"""
        
        data = self.storage.retrieve_json(cid)
        if data and data.get("type", "").startswith("evidence_"):
            return data
        return None
    
    def get_clickable_link(self, cid: str) -> str:
        """Get a clickable IPFS gateway link"""
        return self.storage.get_gateway_url(cid)
