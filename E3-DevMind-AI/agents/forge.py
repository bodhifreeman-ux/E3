"""
Agent #13: FORGE (Code Generator)

Production-quality code generation from specifications.
"""

from agents.base_agent import BaseAgent
from csdl.protocol import CSDLMessage
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class ForgeAgent(BaseAgent):
    """
    FORGE - Code Generator Agent
    
    Capabilities:
    - Feature implementation from specs
    - Code generation from designs
    - Refactoring existing code
    - Bug fixing
    - Boilerplate generation
    - Code modernization
    """
    
    def __init__(self, vllm_client, knowledge_base, config=None):
        super().__init__(
            agent_id="forge",
            agent_name="Forge",
            vllm_client=vllm_client,
            knowledge_base=knowledge_base,
            config=config
        )
    
    def _build_system_context(self) -> Dict[str, Any]:
        return {
            "role": "code_generation",
            "agent_id": "forge",
            "agent_name": "Forge",
            "tier": 4,
            "capabilities": [
                "code_generation",
                "feature_implementation",
                "refactoring",
                "bug_fixing",
                "boilerplate_generation"
            ],
            "specialization": "production_code_generation"
        }
    
    async def process_csdl(
        self,
        message: CSDLMessage,
        context: Optional[Dict[str, Any]] = None
    ) -> CSDLMessage:
        """Generate production-quality code"""
        
        query_type = message.content.get("query_type", "code_generation")
        
        if query_type == "feature_implementation":
            result = await self._implement_feature(message.content)
        elif query_type == "refactoring":
            result = await self._refactor_code(message.content)
        elif query_type == "bug_fix":
            result = await self._fix_bug(message.content)
        else:
            result = await self._generate_code(message.content)
        
        from csdl.protocol import CSDLProtocol
        
        return CSDLProtocol.create_response(
            content_csdl=result,
            sender_id=self.agent_id,
            in_response_to=message.message_id,
            recipient_id=message.sender_id
        )
    
    async def _implement_feature(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Implement feature from specification"""
        
        spec = query_csdl.get("specification", {})
        
        implementation_query = {
            "semantic_type": "feature_implementation",
            "task": "feature_implementation",
            "specification": spec,
            "generate": ["code", "tests", "documentation"],
            "language": query_csdl.get("language", "python"),
            "style_guide": query_csdl.get("style", "pep8")
        }
        
        implementation = await self._call_vllm(implementation_query, temperature=0.2)
        
        return {
            "semantic_type": "implementation_result",
            "code": implementation.get("code", ""),
            "tests": implementation.get("tests", ""),
            "documentation": implementation.get("docs", ""),
            "dependencies": implementation.get("dependencies", [])
        }
    
    async def _refactor_code(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor existing code"""
        
        code = query_csdl.get("code", "")
        
        refactor_query = {
            "semantic_type": "code_refactoring",
            "task": "code_refactoring",
            "code": code,
            "objectives": query_csdl.get("objectives", [
                "improve_readability",
                "reduce_complexity",
                "enhance_maintainability"
            ])
        }
        
        refactored = await self._call_vllm(refactor_query, temperature=0.2)
        
        return {
            "semantic_type": "refactoring_result",
            "refactored_code": refactored.get("code", ""),
            "changes_made": refactored.get("changes", []),
            "improvements": refactored.get("improvements", {})
        }
    
    async def _fix_bug(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """Fix bug in code"""
        
        bug_report = query_csdl.get("bug", {})
        
        fix_query = {
            "semantic_type": "bug_fix",
            "task": "bug_fixing",
            "bug_report": bug_report,
            "code": query_csdl.get("code", "")
        }
        
        fix = await self._call_vllm(fix_query, temperature=0.2)
        
        return {
            "semantic_type": "bug_fix_result",
            "fixed_code": fix.get("code", ""),
            "root_cause": fix.get("root_cause", ""),
            "fix_explanation": fix.get("explanation", "")
        }
    
    async def _generate_code(self, query_csdl: Dict[str, Any]) -> Dict[str, Any]:
        """General code generation"""
        
        code_query = {
            "semantic_type": "code_generation",
            "task": "code_generation",
            "requirements": query_csdl
        }
        
        code = await self._call_vllm(code_query, temperature=0.2)
        
        return code
