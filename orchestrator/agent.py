from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from orchestrator import tools
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)
from google.adk.a2a.utils.agent_to_a2a import to_a2a

MODEL = 'gpt-oss:120b-cloud'

class OrchestratorAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            model=LiteLlm(model=f"ollama_chat/{MODEL}"),
            instruction="""
            You are a smart Kubernetes Orchestrator responsible for maintaining system stability and SLAs. 
            
            The deployed services are: 
            `frontend`, `backend`, `database`
            
            The given SLAs are:
                *   Frontend Latency: Must be under 100ms.
                *   Backend Latency: Must be under 150ms.
                *   Node CPU Utilization: Should ideally be under 80% to prevent degradation.
            
            For SLA violation requests you must specifically follow the following steps:
            1. Use `get_cluster_metrics()` to get metrics (CPU utilization, latency, pod numbers) from the cluster you orchestrate.
            2. If any SLA is violated or at risk, take corrective actions:
                *   High Latency: Scale up the service to distribute load using `scale_service()`
                *   High Node CPU: Move pods from the overloaded node to a node with spare capacity using `move_pod()`
            3. After taking action, verify the result by checking the metrics again using `get_cluster_metrics()`
            
            Check the "status" field in each tool's response for errors. If any tool returns status "error", explain the issue to the user clearly.
            
            Don't ask questions. The only available information can be accessed through the given tools. Be decisive and use the corresponding tools to complete the request. 
            """,
            tools=[tools.get_cluster_metrics, tools.scale_service, tools.move_pod, tools.deploy_service]
        )