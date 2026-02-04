from orchestrator.agent import OrchestratorAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

oa = OrchestratorAgent()

app = to_a2a(oa, port=8001)