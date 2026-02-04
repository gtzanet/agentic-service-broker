from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from resource_provider import tools
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)
from google.adk.a2a.utils.agent_to_a2a import to_a2a

MODEL = 'gpt-oss:120b-cloud'

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