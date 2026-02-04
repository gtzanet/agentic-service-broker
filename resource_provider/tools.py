# --- RPA Tools ---

def evaluate_service_cost(cpu_request: float, memory_request: float) -> dict:
    """Evaluates the cost and energy consumption of a service based on its resource requirements.
    
    Args:
        cpu_request: CPU units requested.
        memory_request: Memory units requested.
        
    Returns:
        dict: Estimated cost and energy metrics.
    """
    print(f"\n[Tool Call] evaluate_service_cost(cpu={cpu_request}, mem={memory_request})")
    
    # Theoretical pricing/energy model
    cost_per_cpu = 10.0
    cost_per_mem = 5.0
    energy_per_cpu = 50.0 # Watts
    energy_per_mem = 10.0 # Watts
    
    estimated_cost = (cpu_request * cost_per_cpu) + (memory_request * cost_per_mem)
    estimated_energy = (cpu_request * energy_per_cpu) + (memory_request * energy_per_mem)
    
    return {
        "status": "ok",
        "result": {
            "estimated_cost_per_hour": estimated_cost,
            "estimated_power_watts": estimated_energy,
            "viability": "High" if estimated_cost < 100 else "Medium" # Simple logic
        }
    }
