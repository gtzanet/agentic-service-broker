from resource_provider.agent import ResourceProviderAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.runners import InMemoryRunner

config = {
    "oa_host": "0.0.0.0",
    "oa_port": 8001
}
rpa = ResourceProviderAgent(config)

runner = InMemoryRunner(agent=rpa)
print("Resource Provider Agent initialized with Ollama.")

import asyncio

async def run_rpa():
    print("Starting Orchestrator run...")
    # Pass the input as a keyword argument
    result = await runner.run_debug(
        "Deploy a high-performance web service. It requires around 2 CPUs and 2GB of Memory. Target latency is < 50ms."
    )
    print("\nAgent Output:")
    print(result)

asyncio.run(run_rpa())

#app = to_a2a(rpa, port=8002)