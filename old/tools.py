from k8s_sim import Cluster
import json

cluster = Cluster() 

# --- OA Tools ---

def get_cluster_metrics() -> dict:
    """Retrieves the current performance metrics of the Kubernetes cluster.
    
    Returns:
        dict: A dictionary containing metrics for nodes, services, and the cluster summary.
              Includes CPU usage, latency, and pod counts.
    """
    print("\n[Tool Call] get_cluster_metrics")
    try:
        metrics = cluster.get_metrics()
        return {"status": "ok", "result": metrics}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def scale_service(service_name: str, replicas: int) -> dict:
    """Scales a specific service to a target number of replicas.
    
    Args:
        service_name: The name of the service to scale (e.g., 'frontend', 'backend').
        replicas: The desired number of replicas.
        
    Returns:
        dict: A status-aware response with keys `status` and `message` or `error`.
    """
    print(f"\n[Tool Call] scale_service(service_name='{service_name}', replicas={replicas})")
    try:
        cluster.scale_service(service_name, replicas)
        return {"status": "ok", "message": f"Successfully scaled {service_name} to {replicas} replicas."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def move_pod(pod_id: str, target_node: str) -> dict:
    """Moves a specific pod to a different node.
    
    Args:
        pod_id: The unique identifier of the pod to move.
        target_node: The name of the destination node (e.g., 'node-1').
        
    Returns:
        dict: A status-aware response with keys `status` and `message` or `error`.
    """
    print(f"\n[Tool Call] move_pod(pod_id='{pod_id}', target_node='{target_node}')")
    try:
        cluster.move_pod(pod_id, target_node)
        return {"status": "ok", "message": f"Successfully moved pod {pod_id} to {target_node}."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def deploy_service(name: str, replicas: int, cpu_request: float, memory_request: float) -> dict:
    """Deploys a new service to the cluster.
    
    Args:
        name: The name of the new service.
        replicas: Number of replicas to start.
        cpu_request: CPU units required per pod.
        memory_request: Memory units required per pod.
    
    Returns:
        dict: Status message.
    """
    print(f"\n[Tool Call] deploy_service(name='{name}', ...)")
    try:
        cluster.deploy_service(name, replicas, cpu_request, memory_request)
        return {"status": "ok", "message": f"Successfully deployed service '{name}'."}
    except Exception as e:
        return {"status": "error", "error": str(e)}

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
