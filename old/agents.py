from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
import tools
from k8s_sim import Cluster
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

# --- A2A Tool for RPA ---

async def talk_to_orchestrator(message: str) -> str:
    """Sends a message to the Orchestrator Agent and returns its response.
    Use this to request deployments or query cluster status.
    """
    print(f"\n[RPA -> OA] Sending message: {message}")
    
    try:
        # Use run_debug (async) to communicate with OA
        # Since this tool is async, we can await it directly
        # assuming the runner executing RPA handles async tools.
        response = await orchestrator_runner.run_debug(message)
        
        # response from run_debug is likely the final result or events
        # Let's convert to string
        final_text = str(response)
    except Exception as e:
        final_text = f"Error communicating with OA: {e}"

    print(f"[OA -> RPA] Response: {final_text}")
    return final_text

# --- Resource Provider Agent (RPA) ---
class ResourceProviderAgent(LlmAgent):
    def __init__(self,config):
        orchestrator_agent = RemoteA2aAgent(
                name="orchestrator_agent",
                description="Remote orchestrator agent from external vendor that is responsible for orchestrating the cluster.",
                # Point to the agent card URL - this is where the A2A protocol metadata lives
                agent_card=f"http://{config['oa_host']}:{config['oa_port']}{AGENT_CARD_WELL_KNOWN_PATH}",
            )
        super().__init__(
            name="ResourceProvider",
            model=LiteLlm(model=f"ollama_chat/{MODEL}"),
            instruction="""
            You are a Resource Provider Agent (RPA).
            Your goal is to evaluate service deployment requests based on cost and energy, and then request their deployment to the Orchestrator.

            Capabilities:
            1.  Evaluate: When given service specs (CPU, Memory), use `evaluate_service_cost()` to see if they are viable.
            2.  Deploy: If a service is viable (Cost < $100/hr, or as requested), use orchestrator_agent subagent to ask the Orchestrator to deploy it. Provide the given requirements (Latency, Request rate, Availability) to the Orchestrator clearly.

            If the user asks you to deploy something, evaluate it first. If good, contact the Orchestrator.
            """,
            tools=[tools.evaluate_service_cost],
            sub_agents=[orchestrator_agent]
        )