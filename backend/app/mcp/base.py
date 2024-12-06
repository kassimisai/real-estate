from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from enum import Enum

class AgentState(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"

class AgentContext(BaseModel):
    agent_id: str
    agent_type: str
    state: AgentState = AgentState.IDLE
    memory: Dict[str, Any] = {}
    tools: List[str] = []
    capabilities: List[str] = []

class AgentMessage(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}
    source_agent: str
    target_agent: Optional[str] = None

class MCPController:
    def __init__(self):
        self.agents: Dict[str, AgentContext] = {}
        self.message_queue: List[AgentMessage] = []
    
    def register_agent(self, agent_context: AgentContext):
        self.agents[agent_context.agent_id] = agent_context
    
    def send_message(self, message: AgentMessage):
        self.message_queue.append(message)
    
    def get_agent_context(self, agent_id: str) -> Optional[AgentContext]:
        return self.agents.get(agent_id)
    
    def update_agent_state(self, agent_id: str, state: AgentState):
        if agent_id in self.agents:
            self.agents[agent_id].state = state
    
    def process_messages(self):
        while self.message_queue:
            message = self.message_queue.pop(0)
            # Process message based on target agent and content
            # Implement message routing and handling logic here
            pass
