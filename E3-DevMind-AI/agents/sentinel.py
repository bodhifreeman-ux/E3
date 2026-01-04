"""
Agent #16: SENTINEL (Security Guardian)

Security across all E3 systems.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class SentinelAgent(BaseAgent):
    """SENTINEL - Security Guardian Agent"""
    
    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="sentinel",
            agent_name="Sentinel",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
    
    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "security",
            "agent_id": "sentinel",
            "agent_name": "Sentinel",
            "tier": 4,
            "capabilities": [
                "vulnerability_scanning",
                "threat_detection",
                "compliance_checking",
                "security_best_practices"
            ]
        }
    
    async def process_csdl(self, message: CSDLMessage, context: Optional[Dict[str, Any]] = None) -> CSDLMessage:
        query_type = message.content.get("query_type", "security_scan")
        
        if query_type == "security_scan":
            result = await self._security_scan(message.content)
        elif query_type == "threat_detection":
            result = await self._detect_threats(message.content)
        else:
            result = await self._check_compliance(message.content)
        
        from csdl.protocol import CSDLProtocol
        return CSDLProtocol.create_response(
            content_csdl=result, sender_id=self.agent_id,
            in_response_to=message.message_id, recipient_id=message.sender_id
        )
    
    async def _security_scan(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        code = query_csdl.get("code", "")
        scan_query = {
            "semantic_type": "security_scan",
            "task": "security_vulnerability_scan",
            "code": code,
            "check_for": ["injection", "xss", "csrf", "authentication", "encryption"]
        }
        scan = await self._call_vllm(scan_query, temperature=0.2)
        return {"semantic_type": "scan_result", "vulnerabilities": scan.get("vulnerabilities", [])}
    
    async def _detect_threats(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        system = query_csdl.get("system", {})
        threat_query = {
            "semantic_type": "threat_detection",
            "task": "threat_detection",
            "system": system
        }
        threats = await self._call_vllm(threat_query, temperature=0.2)
        return {"semantic_type": "threat_result", "threats": threats}
    
    async def _check_compliance(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_vllm({
            "semantic_type": "compliance_check",
            "task": "compliance_checking",
            "subject": query_csdl
        }, temperature=0.2)
